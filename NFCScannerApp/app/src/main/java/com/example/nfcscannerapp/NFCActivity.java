package com.example.nfcscannerapp;

import android.app.PendingIntent;
import android.content.Intent;
import android.content.IntentFilter;
import android.nfc.NdefMessage;
import android.nfc.NdefRecord;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.os.Bundle;
import android.os.Parcelable;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class NFCActivity extends AppCompatActivity {
    private NfcAdapter nfcAdapter;

    String endPoint;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_nfc);

        endPoint = getIntent().getStringExtra("endPoint");

        nfcAdapter = NfcAdapter.getDefaultAdapter(this);

    }

    @Override
    protected void onResume() {
        super.onResume();
        Intent intent = new Intent(this, getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_MUTABLE);
        IntentFilter[] filters = new IntentFilter[]{ new IntentFilter(NfcAdapter.ACTION_TAG_DISCOVERED) };
        nfcAdapter.enableForegroundDispatch(this, pendingIntent, filters, null);
    }

    @Override
    protected void onPause() {
        super.onPause();
        nfcAdapter.disableForegroundDispatch(this);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);

        if (NfcAdapter.ACTION_NDEF_DISCOVERED.equals(intent.getAction()) ||
                NfcAdapter.ACTION_TAG_DISCOVERED.equals(intent.getAction())) {

            Parcelable[] rawMsgs = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES);
            if (rawMsgs != null && rawMsgs.length > 0) {
                NdefMessage msg = (NdefMessage) rawMsgs[0];
                NdefRecord record = msg.getRecords()[0];

                try {
                    byte[] payload = record.getPayload();

                    // Text encoding: payload[0] bit 7 == 0 => UTF-8, else UTF-16
                    String textEncoding = ((payload[0] & 0x80) == 0) ? "UTF-8" : "UTF-16";

                    // Language code length
                    int languageCodeLength = payload[0] & 0x3F;

                    // Actual text
                    String text = new String(payload, languageCodeLength + 1,
                            payload.length - languageCodeLength - 1, textEncoding);

                    if (Utillities.isValidCredentials(text)){
                        Intent intent1 = new Intent(NFCActivity.this, SendDataActivity.class);
                        intent1.putExtra("scannedText" , text);
                        intent1.putExtra("endPoint", endPoint);
                        startActivity(intent1);
                    }else {
                        Toast.makeText(this, "No valid election credentials found", Toast.LENGTH_LONG).show();
                    }

                } catch (Exception e) {
                    Toast.makeText(this, "Error reading tag", Toast.LENGTH_SHORT).show();
                }
            }
        }
    }
}