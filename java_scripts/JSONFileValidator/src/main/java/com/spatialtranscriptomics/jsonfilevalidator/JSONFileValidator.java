/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package com.spatialtranscriptomics.jsonfilevalidator;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.bind.DatatypeConverter;
import org.apache.commons.io.IOUtils;

/**
 *
 * @author joelsjostrand
 */
public class JSONFileValidator {
    
           
    public static boolean isValidJSON(JsonParser parser, boolean checkShallowJSON) {
        boolean valid = false;
        try {
            JsonToken token;
            int i = 0;
            while ((token = parser.nextToken()) != null) {
                if (checkShallowJSON && token.name().equals("FIELD_NAME")) {
                    token = parser.nextToken();
                    switch (token.name()) {
                        case "VALUE_STRING":
                            String txt = parser.getText();
                            if (txt.length() > 100000) {
                                System.out.println("Saving to " + (i) + "tmp");
                                File f = new File("" + (i++) + ".tmp");
                                byte[] bytes = DatatypeConverter.parseBase64Binary(txt);
                                FileOutputStream output = new FileOutputStream(f);
                                IOUtils.write(bytes, output);
                                output.close();
                            } else {
                                System.out.println(parser.getText());
                            }
                            break;
                        case "VALUE_NUMBER_INT":
                            System.out.println(parser.getLongValue());
                            break;
                        default:
                            break;
                    }
                }
            }
            valid = true;
        } catch (JsonParseException jpe) {
            jpe.printStackTrace();
        } catch (IOException ioe) {
            ioe.printStackTrace();
        }

        return valid;
    }

    public static void main(String[] args) {
        if (args == null || args.length == 0) {
            System.out.println("Input: <Either a JSON file or a JSON string> <true/false for checking shallow JSON>");
            return;
        }
        try {
            File f = new File(args[0]);
            boolean b = Boolean.parseBoolean(args.length > 1 ? args[1] : "false");
            if(f.exists() && !f.isDirectory()) {
                System.out.println(isValidJSON(new JsonFactory().createJsonParser(f), b));
            } else {
                System.out.println(isValidJSON(new JsonFactory().createJsonParser(args[0]), b));
            }
        } catch (IOException ex) {
        }
    }
    
}
