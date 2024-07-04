package wallpaper;

/**
 * Huang et al (2015) "Scalable and Precise Taint Analysis for Android".
 * WallpapersMain leaks the device identifier
 * (the source) to a content server (the sink) in a URL.
 */
public class WallpapersMain extends Activity {
    private String BASE_URL, deviceId;
    private int pageNum, catId;
    private DisplayMetrics metrics;
    private WebView browser1;

    protected void onCreate(Bundle b) {
        start();
    }

    protected void onActivityResult(int rq, int rs, Intent i) {
        navigate();
    }

    private void start() {
        BASE URL = "getWallpapers_Android2/";
        TelephonyManager mgr = (TelephonyManager) this.getSystemService("phone");
        deviceId = mgr.getDeviceId(); // source
    }

    private void navigate() {
        String str = BASE_URL + pageNum + "/" + catId + "/"
                + deviceId + "/" + metrics.widthPixels + "/" +
                metrics.heightPixels;
        browser1.loadUrl(str); // sink
    }
}