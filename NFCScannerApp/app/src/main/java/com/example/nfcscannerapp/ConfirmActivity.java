package com.example.nfcscannerapp;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class ConfirmActivity extends AppCompatActivity {


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_confirm);
        String endPoint = getIntent().getStringExtra("endPoint");
        String Hash;
        TextView LinkCode = findViewById(R.id.LinkCodeText);
        try {
            Hash = Utillities.sha256First4(endPoint);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        Button BackButton = findViewById(R.id.ConfirmBack);
        BackButton.setOnClickListener(v -> {
            Intent intent = new Intent(ConfirmActivity.this, ScannerActivity.class);
            startActivity(intent);
        });

        Button ConfrimButton = findViewById(R.id.ConfirmMatch);
        ConfrimButton.setOnClickListener(v -> {
            Intent intent = new Intent(ConfirmActivity.this, NFCActivity.class);
            intent.putExtra("endPoint" , endPoint);
            startActivity(intent);
        });

        LinkCode.setText(Hash);

    }
}