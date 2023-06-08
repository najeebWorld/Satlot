package com.example.satlot;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.AppCompatButton;

import android.widget.Toast;

import okhttp3.*;

import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.telecom.Call;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.Serializable;
import java.lang.reflect.Type;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.Map;

import android.util.Base64;
import android.view.View;
import android.widget.ImageView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    // handle change of pic initialisation
    private static final int REQUEST_TAKE_PHOTO = 1;
    private static final int REQUEST_SELECT_PICTURE = 2;

    String detected_base64 = ""; // Store the data returned from server
    List<Map<String, Integer>> starsList; // Store the detected stars info list
    String original_base64 = ""; // Store the original image in base64

    //Declare Buttons
    AppCompatButton take_picture;
    AppCompatButton open_gallery;
    ImageView capturedImage;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Buttons
        take_picture = findViewById(R.id.TakeLive);
        open_gallery = findViewById(R.id.OpenGallery);
        capturedImage = findViewById(R.id.captured_image);

        take_picture.setOnClickListener(this);
        open_gallery.setOnClickListener(this);
    }

    // Override the 'onClick' method, divided by button id
    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.TakeLive:
                open_camera();
                break;
            case R.id.OpenGallery:
                open_storage();
            default:
                break;
        }

    }

    private void open_storage() { // Choose picture from storage
        Intent selectPicture = new Intent();
        selectPicture.setType("image/*");
        selectPicture.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(Intent.createChooser(selectPicture, "Select Picture"), REQUEST_SELECT_PICTURE);
    }

    private void open_camera() { // Take Picture

        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        try {
            startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
        } catch (ActivityNotFoundException e) {
            System.out.println(e);
        }
    }


    // Function that called when image is selected. Both for camera and storage
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode == RESULT_OK) {
            if (requestCode == REQUEST_TAKE_PHOTO) // Photo captured from camera
            {
                Bundle extras = data.getExtras();
                Bitmap bitmap = (Bitmap) extras.get("data");
                int width = bitmap.getWidth();
                int height = bitmap.getHeight();
                // Convert bitmap to byte array
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, byteArrayOutputStream);
                byte[] byteArray = byteArrayOutputStream.toByteArray();

                // Encode byte array to Base64 string
                original_base64 = Base64.encodeToString(byteArray, Base64.DEFAULT);
                String size = "(" + height + "," + width + ")";
                getCircledStars(original_base64, size);

            } else if (requestCode == REQUEST_SELECT_PICTURE) // Photo selected from gallery
            {
                Uri selectedImageUri = data.getData();

                try {
                    Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), selectedImageUri);
                    int width = bitmap.getWidth();
                    int height = bitmap.getHeight();
                    // Convert bitmap to byte array
                    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, byteArrayOutputStream);
                    byte[] byteArray = byteArrayOutputStream.toByteArray();

                    // Encode byte array to Base64 string
                    original_base64 = Base64.encodeToString(byteArray, Base64.DEFAULT);

                    String size = "(+" + height + "," + width + ")";
                    getCircledStars(original_base64, size);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }


    public void getCircledStars(String imgStr, String size) { // External server function call
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // Create URL
                    URL url = new URL("http://10.0.0.9:5000/circle_stars");
                    // Create connection
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json; utf-8");
                    conn.setRequestProperty("Accept", "application/json");
                    conn.setDoOutput(true);
                    conn.setDoInput(true);

                    // Create the JSON payload
                    JSONObject jsonParam = new JSONObject();
                    jsonParam.put("img_str", imgStr);
                    jsonParam.put("size", size);

                    // Write data
                    OutputStream os = conn.getOutputStream();
                    byte[] input = jsonParam.toString().getBytes("utf-8");
                    os.write(input, 0, input.length);
                    os.close();

                    // Read response
                    InputStream inputStream = conn.getInputStream();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, "utf-8"));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();
                    inputStream.close();

                    // Process the response
                    JSONArray jsonArrResponse = new JSONArray(response.toString());
                    JSONObject jsonResponse = jsonArrResponse.getJSONObject(0);
                    String stars = jsonResponse.getString("stars");
                    String image = jsonResponse.getString("image");

                    // Assign the retrieved values to the variables
                    starsList = new Gson().fromJson(stars, new TypeToken<List<Map<String, Integer>>>() {
                    }.getType());
                    detected_base64 = image;

                    System.out.println(starsList.toString());
                    System.out.println(detected_base64);

                    conn.disconnect();
                    openImageDisplayActivity();

                } catch (Exception e) {
                    e.printStackTrace();
                    ShowError("Error while processing image"); // Error toast
                }
            }
        });

        thread.start();
    }

    public void ShowError(String msg) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, msg, Toast.LENGTH_SHORT).show();
            }
        });
    }


    private void openImageDisplayActivity() {
        try {
            // Create temporary files to store the base64 strings
            File originalFile = createTempFile("original", ".txt");
            File detectedFile = createTempFile("detected", ".txt");

            // Write the base64 strings to the files
            writeStringToFile(originalFile, original_base64);
            writeStringToFile(detectedFile, detected_base64);

            // Create an intent to start the DisplayPicture activity
            Intent intent = new Intent(MainActivity.this, DisplayPicture.class);
            intent.putExtra("original", originalFile.getAbsolutePath());
            intent.putExtra("detected", detectedFile.getAbsolutePath());
            intent.putExtra("stars", (Serializable) starsList);
            startActivity(intent);
        } catch (IOException e) {
            e.printStackTrace();
            ShowError("Error while passing intent"); // Error toast
        }
    }

    private File createTempFile(String prefix, String extension) throws IOException {
        File tempDir = getCacheDir();
        return File.createTempFile(prefix, extension, tempDir);
    }

    private void writeStringToFile(File file, String data) throws IOException {
        FileOutputStream outputStream = new FileOutputStream(file);
        outputStream.write(data.getBytes());
        outputStream.close();
    }
}



