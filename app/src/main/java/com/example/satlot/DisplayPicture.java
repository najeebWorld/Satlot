package com.example.satlot;

import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.widget.ImageView;

import androidx.appcompat.app.AppCompatActivity;

public class DisplayPicture extends AppCompatActivity {

    private ImageView imageDisplay;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display_picture);

        imageDisplay = findViewById(R.id.image_display);

        // Retrieve the image URI or bitmap from the intent extras
        if (getIntent().hasExtra("imageBitmap")) {
            Bitmap imageBitmap = getIntent().getParcelableExtra("imageBitmap");
            imageDisplay.setImageBitmap(imageBitmap);
        } else if (getIntent().hasExtra("imageUri")) {
            String imageUriString = getIntent().getStringExtra("imageUri");
            Uri imageUri = Uri.parse(imageUriString);
            imageDisplay.setImageURI(imageUri);
        }
    }
}
