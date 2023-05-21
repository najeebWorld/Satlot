package com.example.satlot;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.AppCompatButton;

import okhttp3.*;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.telecom.Call;
import android.util.Base64;
import android.view.View;
import android.widget.ImageView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    // handle change of pic initialisation
    private static final int REQUEST_TAKE_PHOTO = 1;
    private static final int REQUEST_SELECT_PICTURE = 2;

    String detected_base64 = "default";
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
                String encodedImage = Base64.encodeToString(byteArray, Base64.DEFAULT);
                String size = "(" + height + "," + width + ")";

                // SEND TO OFEK'S FUNCTION
                try {
                    postRequest(encodedImage, size); // Call to GCP function- identify objects
                    while (detected_base64 == "default") {
                    }
                    if (detected_base64 != "error") {
                        // Decode the Base64 string to a byte array
                        byte[] decodedBytes = Base64.decode(detected_base64, Base64.DEFAULT);

                        // Create a Bitmap from the byte array
                        Bitmap newbitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
                        openImageDisplayActivity(newbitmap);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                System.out.println("The new picture in base64:");
                System.out.println(detected_base64);
                System.out.println("*******************************************");

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
                    String encodedImage = Base64.encodeToString(byteArray, Base64.DEFAULT);

                    String size = "(+" + height + "," + width + ")";
                    // SEND TO OFEK'S FUNCTION
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private void openImageDisplayActivity(Bitmap imageBitmap) {
        Intent intent = new Intent(MainActivity.this, DisplayPicture.class);
        intent.putExtra("imageBitmap", imageBitmap);
        startActivity(intent);
    }

    private void openImageDisplayActivity(Uri imageUri) {
        Intent intent = new Intent(MainActivity.this, DisplayPicture.class);
        intent.putExtra("imageUri", imageUri.toString());
        startActivity(intent);
    }


    public void postRequest(String imgStr, String size) throws IOException, JSONException {
        OkHttpClient client = new OkHttpClient();

        // Create the JSON payload
        JSONObject payload = new JSONObject();
        payload.put("img_str", imgStr);
        payload.put("size", size);

        // Convert the JSON payload to a byte array
        byte[] payloadBytes = payload.toString().getBytes("UTF-8");


        System.out.println("&&&&&&&&&&&&&&&&&&&&&&&&7");
        System.out.println(payloadBytes);
        System.out.println("&&&&&&&&&&&&&&&&&&&&&&&&&");

        RequestBody body = RequestBody.create(
                MediaType.parse("application/json; charset=utf-8"), payloadBytes);

        Request request = new Request.Builder()
                .url("https://europe-west2-satlot-app.cloudfunctions.net/circle-stars")
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onResponse(@NonNull okhttp3.Call call, @NonNull Response response) throws IOException {
                System.out.println("********************");
                System.out.println("OnResponse");
                if (response.isSuccessful()) {
                    detected_base64 = response.body().string();
                    System.out.println("********************");
                    System.out.println("sUCCESSFULResponse");
                    // Use the response
                } else {
                    System.out.println("********************");
                    System.out.println("fAILResponse");
                    detected_base64 = "error";
                    // Handle the error
                }
            }

            @Override
            public void onFailure(@NonNull okhttp3.Call call, @NonNull IOException e) {
                System.out.println("********************");
                System.out.println("OnfAILURE");
                e.printStackTrace();
            }
        });
    }
}



