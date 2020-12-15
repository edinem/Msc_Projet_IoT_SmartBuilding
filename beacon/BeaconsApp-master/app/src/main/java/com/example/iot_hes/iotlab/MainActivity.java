// -*- mode: java -*-
package com.example.iot_hes.iotlab;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.InputFilter;
import android.text.Spanned;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;
import java.util.UUID;

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

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "IoTLab";
    private static final String VERSION = "0.1.9";

    TextView PositionText;
    EditText Percentage;
    Button   IncrButton;
    Button   DecrButton;
    Button   LightButton;
    Button   StoreButton;
    Button   RadiatorButton;

    // In the "OnCreate" function below:
    // - TextView, EditText and Button elements are linked to their graphical parts (Done for you ;) )
    // - "OnClick" functions for Increment and Decrement Buttons are implemented (Done for you ;) )
    //
    // IoT Lab BeaconsApp minimal implementation:
    // - detect the closest Beacon and figure out the current Room
    //
    // TODO List for the whole project:
    // - Set the PositionText with the Room name
    // - Implement the "OnClick" functions for LightButton, StoreButton and RadiatorButton

    private BeaconManager beaconManager;
    private BeaconRegion region;
    private String gatewayAddress;
    // private static Map<Integer, String> rooms;
    static String currentRoom;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        gatewayAddress = "http://192.168.0.194:5001";
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
        LightButton    =  findViewById(R.id.LightButton);
        StoreButton    =  findViewById(R.id.StoreButton);
        RadiatorButton =  findViewById(R.id.RadiatorButton);

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
                        currentRoom = Integer.toString(nearestBeacon.getMinor());
                        String msg = "Room " +  currentRoom + "\n(major ID " +
                            Integer.toString(nearestBeacon.getMajor()) + ")";
                        Log.d(TAG, msg);
                        PositionText.setText(msg);
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



        LightButton.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {
                RequestBody body = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), preparePayload(currentRoom, Percentage.getText().toString()));
                System.out.println(body.toString());
                final Request request = new Request.Builder()
                        .url(gatewayAddress+"/light").post(body).build();
                new MyAsyncTask().execute(request);
            }
        });



        StoreButton.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {
                RequestBody body = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), preparePayload(currentRoom, Percentage.getText().toString()));
                System.out.println(body.toString());
                final Request request = new Request.Builder()
                        .url(gatewayAddress+"/store").post(body).build();
                new MyAsyncTask().execute(request);
            }
        });



        RadiatorButton.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {
                RequestBody body = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), preparePayload(currentRoom, Percentage.getText().toString()));
                System.out.println(body.toString());
                final Request request = new Request.Builder()
                        .url(gatewayAddress+"/radiator").post(body).build();
                new MyAsyncTask().execute(request);
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

        @Override
        protected void onPostExecute(Response response) {
            super.onPostExecute(response);
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
