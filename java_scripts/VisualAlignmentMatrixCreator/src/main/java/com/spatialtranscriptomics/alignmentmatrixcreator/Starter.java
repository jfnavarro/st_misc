/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package com.spatialtranscriptomics.alignmentmatrixcreator;

import java.awt.BorderLayout;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;
import javax.swing.JFrame;

/**
 *
 * @author joelsjostrand
 */
public class Starter implements Runnable {
 
    public static void main(String[] args) {
        try {
            BufferedImage ref = ImageIO.read(new File("/Users/joelsjostrand/st/alignment_experiment/niftytest/130219_558894_1F_blue.jpg"));
            BufferedImage target = ImageIO.read(new File("/Users/joelsjostrand/st/alignment_experiment/niftytest/imagealignment.png"));
            Starter s = new Starter(ref, target);
            s.start();
        } catch (IOException ex) {
            Logger.getLogger(Starter.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        
     
    }
    
    
    
    
    private JFrame frame;
    private ZoomAndPanCanvas chart;
    private Thread runThread;
    private boolean running = false;
    private boolean paused = false;
    
    public Starter(BufferedImage ref, BufferedImage target) {
        frame = new JFrame("Zoom and Pan Canvas");
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frame.setIgnoreRepaint(true);
        chart = new ZoomAndPanCanvas(ref, target);
        frame.add(chart, BorderLayout.CENTER);
        frame.pack();
        frame.setVisible(true);
        chart.createBufferStrategy(2);
        
    }

    public void start() {
        running = true;
        paused = false;
        if(runThread == null || !runThread.isAlive())
            runThread = new Thread(this);
        else if(runThread.isAlive())
            throw new IllegalStateException("Thread already started.");
        runThread.start();
    }

    public void stop() {
        if(runThread == null)
            throw new IllegalStateException("Thread not started.");
        synchronized (runThread) {
            try {
                running = false;
                runThread.notify();
                runThread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public void pause() {
        if(runThread == null)
            throw new IllegalStateException("Thread not started.");
        synchronized (runThread) {
            paused = true;
        }
    }

    public void resume() {
        if(runThread == null)
            throw new IllegalStateException("Thread not started.");
        synchronized (runThread) {
            paused = false;
            runThread.notify();
        }
    }

    public void run() {
        long sleep = 0, before;
        while(running) {
            // get the time before we do our game logic
            before = System.currentTimeMillis();
            // move player and do all game logic
            Graphics myGraphics = frame.getGraphics();
            //System.out.println("Rendering!");
            chart.render(myGraphics);
            chart.repaint();
            myGraphics.dispose();
            try {
                // sleep for 100 - how long it took us to do our game logic
                sleep = 25-(System.currentTimeMillis()-before);
                Thread.sleep(sleep > 0 ? sleep : 0);
            } catch (InterruptedException ex) {
            }
            synchronized (runThread) {
                if(paused) {
                    try {
                        runThread.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
        paused = false;
    }
}
