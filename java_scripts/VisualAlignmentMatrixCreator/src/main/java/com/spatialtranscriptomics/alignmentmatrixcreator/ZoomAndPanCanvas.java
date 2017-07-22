package com.spatialtranscriptomics.alignmentmatrixcreator;

import java.awt.*;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;
import javax.swing.*;

/**
 * Canvas displaying a simple drawing: the coordinate-system axes + some points and their coordinates.
 * It is used to demonstrate the Zoom and Pan functionality.
 *
 * @author Sorin Postelnicu.
 * @author  Joel Sjöstrand.
 * @since July 13, 2009
 */

public class ZoomAndPanCanvas extends Canvas {

    /** First time init. */
    private boolean init = true;

    /** For showing coordinates. */
    private Point[] points = {
            new Point(-100, -100),
            new Point(-100, 100),
            new Point(100, -100),
            new Point(100, 100)
    };

    /** Transform and zooming and panning tool. */
    private ZoomAndPanListener zoomAndPanListener;

    /** Reference image. */
    private BufferedImage reference;
    
    /** Target image. target_coords*transform=reference_coords. */ 
    private BufferedImage target;
    
    /**
     * Constructor.
     */
    public ZoomAndPanCanvas(BufferedImage reference, BufferedImage target) {
        this.reference = reference;
        this.target = target;
        this.zoomAndPanListener = new ZoomAndPanListener(this);
        this.addMouseListener(zoomAndPanListener);
        this.addMouseMotionListener(zoomAndPanListener);
        this.addMouseWheelListener(zoomAndPanListener);
    }

    /**
     * Preferred startup size.
     * @return 
     */
    public Dimension getPreferredSize() {
        return new Dimension(1024, 768);
    }
    
    private double refScale;
    
    private static final float ALPHA_MIN = 0.1f;
    private static final float ALPHA_MAX = 0.4f;
    private float alpha = ALPHA_MAX;
    private float alphaDelta = 0.010f;
    private long alphaTime = System.currentTimeMillis();
    

    public void render(Graphics g1) {
        Graphics2D g = (Graphics2D) g1;
        
        // Draw the ref. in the original coordinate system.
        double x2y = this.getWidth() / (double) this.getHeight();
        double refx2y = this.reference.getWidth() / (double) this.reference.getHeight();
        if (refx2y >= x2y) {
            // x-axis dictates.
            this.refScale = this.getWidth() / (double) this.reference.getWidth();
        } else {
            // y-axis dictates.
            this.refScale = this.getHeight() / (double) this.reference.getHeight();
        }
        g.drawImage(this.reference, 0, 0, (int) Math.round(this.reference.getWidth() * this.refScale), (int) Math.round(this.reference.getHeight() * this.refScale), this);
        
        // Update coordinate system to the target's.
        if (init) {
            // Initialize the viewport by moving the origin to the center of the window,
            // and inverting the y-axis to point upwards.
            init = false;
            Dimension d = getSize();
            int xc = d.width / 2;
            int yc = d.height / 2;
            g.translate(xc, yc);
            //g.scale(1, -1);
            // Save the viewport to be updated by the ZoomAndPanListener
            zoomAndPanListener.setCoordTransform(g.getTransform());
        } else {
            // Restore the viewport after it was updated by the ZoomAndPanListener
            g.setTransform(zoomAndPanListener.getCoordTransform());
        }

        // Change alpha in a wave.
        long time = System.currentTimeMillis();
        if (time - this.alphaTime >= 1) {
            this.alpha += alphaDelta;
            if (this.alpha >= ALPHA_MAX) {
                this.alpha = ALPHA_MAX;
                this.alphaDelta = -this.alphaDelta;
            } else if (this.alpha <= ALPHA_MIN) {
                this.alpha = ALPHA_MIN;
                this.alphaDelta = -this.alphaDelta;
            }
            this.alphaTime = time;
        }
        AlphaComposite ac = AlphaComposite.getInstance(AlphaComposite.SRC_OVER, this.alpha);
        g.setComposite(ac);
        g.drawImage(this.target, 0, 0, null);
                
        // Draw the axes
        g.drawLine(-1000, 0, 1000, 0);
        g.drawLine(0, -1000, 0, 1000);
        
        // Draw the points and their coordinates
        g.setColor(Color.red);
        for (int i = 0; i < points.length; i++) {
            Point p = points[i];
            g.drawLine((int)p.getX() - 5, (int)p.getY(), (int)p.getX() + 5, (int)p.getY());
            g.drawLine((int)p.getX(), (int)p.getY() -5, (int)p.getX(), (int)p.getY() + 5);
            //g.drawString("Alpha time: " + this.alphaTime + ", alpha: " + this.alpha + ", alpha delta: " + this.alphaDelta, (float) p.getX(), (float) p.getY());
        }
    }
    
    
    /**
     * Fills the canvas.
     * @param g1 
     */
    public void paint(Graphics g1) {
        this.render(g1);
    }

}