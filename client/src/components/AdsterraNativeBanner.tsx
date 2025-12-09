import { useEffect, useRef } from 'react';

export function AdsterraNativeBanner() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // Create script element
        const script = document.createElement('script');
        script.async = true;
        script.dataset.cfasync = "false";
        script.src = "//pl28218686.effectivegatecpm.com/632d85aa46582f7707b7900d284499a7/invoke.js";

        // Append script to container
        // We append it to the div wrapper to ensure it stays local if possible, 
        // though the script might look for the specific id in the document.
        // The script looks for "container-632d85aa46582f7707b7900d284499a7"
        containerRef.current.appendChild(script);

        return () => {
            // Cleanup if necessary
            if (containerRef.current) {
                containerRef.current.innerHTML = '';
            }
        };
    }, []);

    return (
        <div className="w-full flex justify-center my-4">
            {/* 
         The native banner script looks for a div with a specific ID.
         We must provide that ID exactly.
       */}
            <div ref={containerRef} id="container-632d85aa46582f7707b7900d284499a7"></div>
        </div>
    );
}
