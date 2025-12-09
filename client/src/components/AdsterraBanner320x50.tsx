import { useEffect, useRef } from 'react';

export function AdsterraBanner320x50() {
    const bannerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const banner = bannerRef.current;
        if (!banner) return;

        // Clear previous content
        banner.innerHTML = '';

        // Create a container for the iframe with no border/overflow
        const conf = document.createElement('div');

        // We use a safely jailed iframe approach or direct injection. 
        // Since 'atOptions' is a global variable, we need to be careful.
        // However, usually these scripts use document.write. 
        // The safest way to handle document.write in React is to put it in an iframe.

        const iframe = document.createElement('iframe');
        iframe.style.width = '320px';
        iframe.style.height = '50px';
        iframe.style.border = 'none';
        iframe.style.overflow = 'hidden';
        iframe.title = "Advertisement";

        banner.appendChild(iframe);

        const doc = iframe.contentWindow?.document;
        if (doc) {
            doc.open();
            doc.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <style>body { margin: 0; padding: 0; overflow: hidden; }</style>
        </head>
        <body>
          <script type="text/javascript">
            atOptions = {
              'key' : '3ca7e9faddee246da59595956a5c4122',
              'format' : 'iframe',
              'height' : 50,
              'width' : 320,
              'params' : {}
            };
          </script>
          <script type="text/javascript" src="//www.highperformanceformat.com/3ca7e9faddee246da59595956a5c4122/invoke.js"></script>
        </body>
        </html>
      `);
            doc.close();
        }

        return () => {
            // Cleanup
            if (banner) banner.innerHTML = '';
        };
    }, []);

    return (
        <div className="w-full flex justify-center my-4">
            <div ref={bannerRef} style={{ width: '320px', height: '50px' }} />
        </div>
    );
}
