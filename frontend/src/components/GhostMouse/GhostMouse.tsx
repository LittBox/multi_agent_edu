import { useEffect, useRef } from "react";
import "./GhostMouse.css";

const map = (
  num: number,
  inMin: number,
  inMax: number,
  outMin: number,
  outMax: number
) => {
  return ((num - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
};

const GhostMouse: React.FC = () => {
  const ghostRef = useRef<HTMLDivElement | null>(null);
  const eyesRef = useRef<HTMLDivElement | null>(null);
  const mouthRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mouse = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    };

    let clicked = false;
    let animationId = 0;

    const pos = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    };

    const getMouse = (event: MouseEvent | TouchEvent) => {
      if ("touches" in event && event.touches.length > 0) {
        mouse.x = event.touches[0].pageX;
        mouse.y = event.touches[0].pageY;
        return;
      }

      if ("clientX" in event) {
        mouse.x = event.clientX;
        mouse.y = event.clientY;
      }
    };

    const handleMouseDown = () => {
      clicked = true;
    };

    const handleMouseUp = () => {
      clicked = false;
    };

    const render = () => {
      const ghost = ghostRef.current;
      const eyes = eyesRef.current;
      const mouth = mouthRef.current;

      if (!ghost || !eyes || !mouth) return;

      const distX = mouse.x - pos.x;
      const distY = mouse.y - pos.y;

      const velX = distX / 8;
      const velY = distY / 8;

      pos.x += distX / 10;
      pos.y += distY / 10;

      const skewX = map(velX, 0, 100, 0, -50);
      const scaleY = map(velY, 0, 100, 1, 2);
      const scaleEyeX = map(Math.abs(velX), 0, 100, 1, 1.2);
      let scaleEyeY = map(Math.abs(velX * 2), 0, 100, 1, 0.1);
      let scaleMouth = Math.min(
        Math.max(
          map(Math.abs(velX * 1.5), 0, 100, 0, 10),
          map(Math.abs(velY * 1.2), 0, 100, 0, 5)
        ),
        2
      );

      if (clicked) {
        scaleEyeY = 0.4;
        scaleMouth = -scaleMouth;
      }

      ghost.style.transform = `
        translate(${pos.x}px, ${pos.y}px)
        scale(0.7)
        skew(${skewX}deg)
        rotate(${-skewX}deg)
        scaleY(${scaleY})
      `;

      eyes.style.transform = `
        translateX(-50%)
        scale(${scaleEyeX}, ${scaleEyeY})
      `;

      mouth.style.transform = `
        translate(${-skewX * 0.5 - 10}px)
        scale(${scaleMouth})
      `;

      animationId = requestAnimationFrame(render);
    };

    window.addEventListener("mousemove", getMouse);
    window.addEventListener("touchstart", getMouse);
    window.addEventListener("touchmove", getMouse);
    window.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);

    render();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("mousemove", getMouse);
      window.removeEventListener("touchstart", getMouse);
      window.removeEventListener("touchmove", getMouse);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <>
      <div ref={ghostRef} className="ghost-mouse">
        <div className="ghost-mouse__head">
          <div ref={eyesRef} className="ghost-mouse__eyes"></div>
          <div ref={mouthRef} className="ghost-mouse__mouth"></div>
        </div>

        <div className="ghost-mouse__tail">
          <div className="ghost-mouse__rip"></div>
        </div>
      </div>

      <svg className="ghost-mouse-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="goo">
            <feGaussianBlur
              in="SourceGraphic"
              stdDeviation="10"
              result="ghost-blur"
            />
            <feColorMatrix
              in="ghost-blur"
              mode="matrix"
              values="
                1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0
                0 0 0 16 -7"
              result="ghost-gooey"
            />
          </filter>
        </defs>
      </svg>
    </>
  );
};

export default GhostMouse;