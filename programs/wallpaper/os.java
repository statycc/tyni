package wallpaper;

/* Android OS class stubs */

class Activity {
    public Object getSystemService(String key) {
        Object tm = null;
        if (key.equals("phone")) {
            tm = new TelephonyManager();
        }
        return tm;
    }
}

class DisplayMetrics {
    public int widthPixels;
    public int heightPixels;
}

class WebView {
    public void loadUrl(String url) { /* sink */ }
}

class Bundle {
}

class Intent {
}

class TelephonyManager {
    public String getDeviceId() {
        return "secret";
    }
}