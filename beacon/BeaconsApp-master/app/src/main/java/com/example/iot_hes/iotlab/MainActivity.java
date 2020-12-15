// -*- mode: java -*-
package com.example.iot_hes.iotlab;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.text.InputFilter;
import android.text.Spanned;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.estimote.coresdk.common.config.EstimoteSDK;
import com.estimote.coresdk.common.config.Flags;
import com.estimote.coresdk.common.requirements.SystemRequirementsChecker;
import com.estimote.coresdk.observation.region.beacon.BeaconRegion;
import com.estimote.coresdk.recognition.packets.Beacon;
import com.estimote.coresdk.repackaged.okhttp_v2_2_0.com.squareup.okhttp.MediaType;
import com.estimote.coresdk.repackaged.okhttp_v2_2_0.com.squareup.okhttp.OkHttpClient;
import com.estimote.coresdk.repackaged.okhttp_v2_2_0.com.squareup.okhttp.Request;
import com.estimote.coresdk.repackaged.okhttp_v2_2_0.com.squareup.okhttp.RequestBody;
import com.estimote.coresdk.repackaged.okhttp_v2_2_0.com.squareup.okhttp.Response;
import com.estimote.coresdk.service.BeaconManager;
import com.microsoft.azure.sdk.iot.device.DeviceClient;
import com.microsoft.azure.sdk.iot.device.IotHubClientProtocol;
import com.microsoft.azure.sdk.iot.device.IotHubConnectionStatusChangeCallback;
import com.microsoft.azure.sdk.iot.device.IotHubConnectionStatusChangeReason;
import com.microsoft.azure.sdk.iot.device.IotHubEventCallback;
import com.microsoft.azure.sdk.iot.device.IotHubMessageResult;
import com.microsoft.azure.sdk.iot.device.IotHubStatusCode;
import com.microsoft.azure.sdk.iot.device.Message;
import com.microsoft.azure.sdk.iot.device.transport.IotHubConnectionStatus;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.List;
import java.util.UUID;


public class MainActivity extends AppCompatActivity {
    private static final String TAG = "IoTLab";
    private static final String VERSION = "0.1.9";

    TextView PositionText;
    TextView StatusText;
    EditText Percentage;
    Button   IncrButton;
    Button   DecrButton;
    Button   StoreButton;
    Button   RadiatorButton;

    private DeviceClient client;

    IotHubClientProtocol protocol = IotHubClientProtocol.MQTT;

    private int msgSentCount = 0;
    private Message sendMessage;


    private final Handler handler = new Handler();
    private Thread sendThread;
    private String responseText;
    private String lastException;


    private BeaconManager beaconManager;
    private BeaconRegion region;
    private String gatewayAddress;
    // private static Map<Integer, String> rooms;
    static String currentRoom = "";
    static String lastRoom = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        gatewayAddress = "http://192.168.0.194:5001"; // To change
        OkHttpClient client = new OkHttpClient();

        Log.d(TAG, "Version: "+VERSION);

        if (ActivityCompat.checkSelfPermission(
                this,
                android.Manifest.permission.ACCESS_FINE_LOCATION
        ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
                    2);
        }

        PositionText   =  findViewById(R.id.PositionText);
        Percentage     =  findViewById(R.id.Percentage);
        IncrButton     =  findViewById(R.id.IncrButton);
        DecrButton     =  findViewById(R.id.DecrButton);
        StoreButton    =  findViewById(R.id.StoreButton);
        RadiatorButton =  findViewById(R.id.RadiatorButton);
        StatusText     =  findViewById(R.id.textView);

        Flags.DISABLE_BATCH_SCANNING.set(true);
        Flags.DISABLE_HARDWARE_FILTERING.set(true);

        EstimoteSDK.initialize(getApplicationContext(), //"", ""
                               // These are not needed for beacon ranging
                                "smarthepia-8d8",                    // App ID
                                "771bf09918ceab03d88d4937bdede558"   // App Token
                               );
        EstimoteSDK.enableDebugLogging(true);

        // we want to find all of our beacons on range, so no major/minor is
        // specified. However the student's labo has assigned a given major
        region = new BeaconRegion(TAG, UUID.fromString("B9407F30-F5F8-466E-AFF9-25556B57FE6D"),
                                  null,    // major -- for the students it should be the assigned one 17644
                                  null      // minor
                                  );
        beaconManager = new BeaconManager(this);
        // beaconManager = new BeaconManager(getApplicationContext());

        beaconManager.setRangingListener(new BeaconManager.BeaconRangingListener() {
                @Override
                public void onBeaconsDiscovered(BeaconRegion region, List<Beacon> list) {
                    Log.d(TAG, "Beacons: found " + String.format("%d", list.size()) + " beacons in region "
                          + region.getProximityUUID().toString());

                    if (!list.isEmpty()) {
                        Beacon nearestBeacon = list.get(0);
                        String tmpRoom = currentRoom;
                        currentRoom = Integer.toString(nearestBeacon.getMinor());
                        String msg = "Room " +  currentRoom + "\n(major ID " +
                            Integer.toString(nearestBeacon.getMajor()) + ")";
                        Log.d(TAG, msg);
                        PositionText.setText(msg);
                        start();
                        if(!tmpRoom.equals(currentRoom)){
                            if(!tmpRoom.equals("")) {
                                lastRoom = tmpRoom;
                            }
                            askValues();
                        }
                    }
                }
            });

        beaconManager.setForegroundScanPeriod(2000, 1000);




        // Only accept input values between 0 and 100
        Percentage.setFilters(new InputFilter[]{new InputFilterMinMax("0", "100")});

        IncrButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                int number = Integer.parseInt(Percentage.getText().toString());
                if (number<100) {
                    number++;
                    Log.d(TAG, "Inc: "+String.format("%d",number));
                    Percentage.setText(String.format("%d",number));
                }
            }
        });

        DecrButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                int number = Integer.parseInt(Percentage.getText().toString());
                if (number>0) {
                    number--;
                    Log.d(TAG, "Dec: "+String.format("%d",number));
                    Percentage.setText(String.format("%d",number));
                }
            }
        });

        StoreButton.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {
                RequestBody body = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), preparePayload(currentRoom, Percentage.getText().toString()));
                System.out.println(body.toString());
                final Request request = new Request.Builder()
                        .url(gatewayAddress+"/store").post(body).build();
                new MyAsyncTask().execute(request);
                askValues();
            }
        });



        RadiatorButton.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {
                RequestBody body = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), preparePayload(currentRoom, Percentage.getText().toString()));
                System.out.println(body.toString());
                final Request request = new Request.Builder()
                        .url(gatewayAddress+"/radiator").post(body).build();
                new MyAsyncTask().execute(request);
                askValues();
            }
        });


    }

    // You will be using "OnResume" and "OnPause" functions to resume and pause Beacons ranging (scanning)
    // See estimote documentation:  https://developer.estimote.com/android/tutorial/part-3-ranging-beacons/
    @Override
    protected void onResume() {
        super.onResume();
        SystemRequirementsChecker.checkWithDefaultDialogs(this);

        beaconManager.connect(new BeaconManager.ServiceReadyCallback() {
            @Override
            public void onServiceReady() {
                String msg = "Beacons: start scanning...";
                PositionText.setText(msg);
                Log.d(TAG, msg);
                beaconManager.startRanging(region);
            }
        });
    }


    @Override
    protected void onPause() {
        beaconManager.stopRanging(region);

        super.onPause();

    }

    // Methode permettant de demander les valeurs des stores et des radiateurs au serveur KNX
    private void askValues() {
        final Request request = new Request.Builder()
                .url(gatewayAddress+"/room/"+currentRoom).get().build();
        new MyAsyncTask().execute(request);

    }

    // Methode permettant de parser le JSON reçu comme réponse du serveur KNX contenant les valeurs actuelles des stores et des radiateurs.
    private String parseJson(String jsonString) {
        String value = "";
        try {
            JSONArray jsonArray = new JSONArray(jsonString);
            value = "First blind: " + jsonArray.getString(0) + "\n\n";
            value += "Second blind: " + jsonArray.getString(1) + "\n\n";
            value += "First valve: " + jsonArray.getString(2) + "\n\n";
            value += "Second valve: " + jsonArray.getString(3) + "\n\n";

        } catch (JSONException e) {
            e.printStackTrace();
        }
        return value;
    }

    // Methode permettant de préparer le payload à envoyer au serveur KNX
    private String preparePayload(String room, String pourcentage) {
        return "{" +
                "\"room\": \"" + room + "\"," +
                "\"data\": " + pourcentage + "" +
                "}";
    }

    // Source de la class MyAsyncTask : https://stackoverflow.com/questions/40690004/how-can-i-change-okhttpclient-to-asynctask
    class MyAsyncTask extends AsyncTask<Request, Void, Response> {

        @Override
        protected Response doInBackground(Request... requests) {
            OkHttpClient client = new OkHttpClient();
            Response response = null;
            try {
                response = client.newCall(requests[0]).execute();
            } catch (IOException e) {
                e.printStackTrace();
            }
            return response;
        }

        // Methode exécutée après l'execution de l'AsyncTask
        @Override
        protected void onPostExecute(Response response) {
            super.onPostExecute(response);
            try {
                responseText = response.body().string();
                String textToShow = parseJson(responseText);
                StatusText.setText(textToShow);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void start()
    {
        sendThread = new Thread(new Runnable() {
            public void run()
            {
                try
                {
                    initClient();
                    sendMessages();

                } catch (Exception e)
                {
                    lastException = "Exception while opening IoTHub connection: " + e;
                }
            }
        });

        sendThread.start();
    }


    private void sendMessages()
    {
        String msgStr = "{ \"room\": \""+ currentRoom + "\", \"previousRoom\": \""+ lastRoom + "\"}";
        try
        {
            sendMessage = new Message(msgStr);
            sendMessage.setMessageId(java.util.UUID.randomUUID().toString());
            System.out.println("Message Sent: " + msgStr);
            EventCallback eventCallback = new EventCallback();
            client.sendEventAsync(sendMessage, eventCallback, msgSentCount);
            msgSentCount++;
        }
        catch (Exception e)
        {
            System.err.println("Exception while sending event: " + e);
        }
    }

    private void initClient() throws URISyntaxException, IOException
    {
        client = new DeviceClient("HostName=IoT-Hub-Daniel.azure-devices.net;DeviceId=MyAndroidDevice;SharedAccessKey=eegVMW6q5jKtJn+H7+YBzSauzMvcVo8t/Yp5aftixp4=", protocol);

        try
        {
            client.registerConnectionStatusChangeCallback(new IotHubConnectionStatusChangeCallbackLogger(), new Object());
            client.open();
            MessageCallback callback = new MessageCallback();
            client.setMessageCallback(callback, null);
        }
        catch (Exception e)
        {
            System.err.println("Exception while opening IoTHub connection: " + e);
            client.closeNow();
            System.out.println("Shutting down...");
        }
    }

    class MessageCallback implements com.microsoft.azure.sdk.iot.device.MessageCallback
    {
        public IotHubMessageResult execute(Message msg, Object context)
        {
            System.out.println(
                    "Received message with content: " + new String(msg.getBytes(), Message.DEFAULT_IOTHUB_MESSAGE_CHARSET));
           // TextView txtMsgsReceivedVal = findViewById(R.id.txtMsgsReceivedVal);
           // txtMsgsReceivedVal.setText(Integer.toString(msgReceivedCount));
           // txtLastMsgReceivedVal.setText("[" + new String(msg.getBytes(), Message.DEFAULT_IOTHUB_MESSAGE_CHARSET) + "]");
            return IotHubMessageResult.COMPLETE;
        }
    }

    class EventCallback implements IotHubEventCallback {
        public void execute(IotHubStatusCode status, Object context)
        {
            Integer i = context instanceof Integer ? (Integer) context : 0;
            System.out.println("IoT Hub responded to message " + i.toString()
                    + " with status " + status.name());
        }
    }

    protected static class IotHubConnectionStatusChangeCallbackLogger implements IotHubConnectionStatusChangeCallback
    {
        @Override
        public void execute(IotHubConnectionStatus status, IotHubConnectionStatusChangeReason statusChangeReason, Throwable throwable, Object callbackContext)
        {
            System.out.println();
            System.out.println("CONNECTION STATUS UPDATE: " + status);
            System.out.println("CONNECTION STATUS REASON: " + statusChangeReason);
            System.out.println("CONNECTION STATUS THROWABLE: " + (throwable == null ? "null" : throwable.getMessage()));
            System.out.println();

            if (throwable != null)
            {
                throwable.printStackTrace();
            }

            if (status == IotHubConnectionStatus.DISCONNECTED)
            {
                //connection was lost, and is not being re-established. Look at provided exception for
                // how to resolve this issue. Cannot send messages until this issue is resolved, and you manually
                // re-open the device client
            }
            else if (status == IotHubConnectionStatus.DISCONNECTED_RETRYING)
            {
                //connection was lost, but is being re-established. Can still send messages, but they won't
                // be sent until the connection is re-established
            }
            else if (status == IotHubConnectionStatus.CONNECTED)
            {
                //Connection was successfully re-established. Can send messages.
            }
        }
    }
}


// This class is used to filter input, you won't be using it.

class InputFilterMinMax implements InputFilter {
    private int min, max;

    public InputFilterMinMax(int min, int max) {
        this.min = min;
        this.max = max;
    }

    public InputFilterMinMax(String min, String max) {
        this.min = Integer.parseInt(min);
        this.max = Integer.parseInt(max);
    }

    @Override
    public CharSequence filter(CharSequence source, int start, int end, Spanned dest, int dstart, int dend) {
        try {
            int input = Integer.parseInt(dest.toString() + source.toString());
            if (isInRange(min, max, input))
                return null;
        } catch (NumberFormatException nfe) { }
        return "";
    }

    private boolean isInRange(int a, int b, int c) {
        return b > a ? c >= a && c <= b : c >= b && c <= a;
    }
}
