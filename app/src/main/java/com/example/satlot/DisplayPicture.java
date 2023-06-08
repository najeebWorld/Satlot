package com.example.satlot;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.widget.ImageView;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.AppCompatButton;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.Map;

public class DisplayPicture extends AppCompatActivity implements View.OnClickListener {

    private ImageView imageDisplay;
    CustomAdapter stars_adp;
    ListView stars;
    AppCompatButton proceed;
    String original_base64 = "";
    String detected_base64 = "";
    int chunks_num;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        System.out.println("!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#");
        System.out.println("MOVEDDDDDDDDDDDDDDDDDDDDDDD");
        System.out.println("!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display_picture);

        imageDisplay = findViewById(R.id.image_display);
        stars = findViewById(R.id.object_list);
        stars.setVerticalScrollBarEnabled(true);
        proceed = findViewById(R.id.proceed);

        // Retrieve the image URI or bitmap from the intent extras
        if (getIntent().hasExtra("stars")) {
            List<Map<String, Integer>> starsList = (List<Map<String, Integer>>) getIntent().getSerializableExtra("stars");
            System.out.println("*********************************");
            for (int i = 0; i < starsList.size(); i++) {
                System.out.println("Map " + (i + 1) + ":");
                Map<String, Integer> map = starsList.get(i);
                for (Map.Entry<String, Integer> entry : map.entrySet()) {
                    String key = entry.getKey();
                    Integer value = entry.getValue();
                    System.out.println(key + " = " + value);
                }
                System.out.println();
            }
            System.out.println("*********************************");
            stars_adp = new CustomAdapter(getApplicationContext(), starsList);
            stars.setAdapter(stars_adp);
        }

        if (getIntent().hasExtra("detected")) {
            String detectedFilePath = getIntent().getStringExtra("detected");
            detected_base64 = readFileToString(new File(detectedFilePath));
            byte[] decodedBytes = Base64.decode(detected_base64, Base64.DEFAULT);
            Bitmap bitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
            imageDisplay.setImageBitmap(bitmap);
        }

        if (getIntent().hasExtra("original")) {
            String detectedFilePath = getIntent().getStringExtra("original");
            original_base64 = readFileToString(new File(detectedFilePath));
        }


        proceed.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.proceed:
                //OFEK'S 2ND FUNCTION
                break;
            default:
                break;
        }
    }

    private String readFileToString(File file) {
        try {
            BufferedReader reader = new BufferedReader(new FileReader(file));
            StringBuilder stringBuilder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                stringBuilder.append(line);
            }
            reader.close();
            return stringBuilder.toString();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }
}
