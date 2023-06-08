package com.example.satlot;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.zip.Inflater;

public class CustomAdapter extends BaseAdapter {

    Context ctx;
    LayoutInflater inflater;
    List<Map<String, Integer>> data;

    public CustomAdapter(Context ctx, List<Map<String, Integer>> data) {
        this.ctx = ctx;
        this.inflater = LayoutInflater.from(ctx);
        this.data=data;
    }

    @Override
    public View getView(int i, View view, ViewGroup viewGroup) {
        if (view == null) {
            view = inflater.inflate(R.layout.activity_object_view, viewGroup, false);
        }

        TextView starId = view.findViewById(R.id.starId);
        TextView Xcor = view.findViewById(R.id.starX);
        TextView Ycor = view.findViewById(R.id.starY);
        TextView radius = view.findViewById(R.id.starR);
        TextView brightness = view.findViewById(R.id.starB);

        starId.setText("ID: " + (i + 1));
        Xcor.setText("X pos: " + data.get(i).get("x"));
        Ycor.setText("Y pos: " + data.get(i).get("y"));
        radius.setText("Radius: " + data.get(i).get("r"));
        brightness.setText("Brightness: " + data.get(i).get("b"));

        return view;
    }



    @Override
    public int getCount() {
        return data.size();
    }

    @Override
    public Object getItem(int position) {
        return data.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }
}