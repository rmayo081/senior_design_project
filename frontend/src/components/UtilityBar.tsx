import { useEffect } from 'react';

function UtilityBar() {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://cdn.ncsu.edu/brand-assets/utility-bar/v3/ncstate-utility-bar.js';
        document.body.prepend(script);

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <div id="ncstate-utility-bar" data-prop-show-brick="0" data-prop-cse-id="00578865650663686:7xmauxacbr4" ></div>
    );
}

export default UtilityBar;