import { useState } from "react";
import { motion } from "motion/react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import "../../styles/components/AuthCarousel.css";
import { useNavigate } from "react-router-dom";

// 定义图片资源类型
interface Asset {
  src: string;
  title: string;
}

const ASSETS: Asset[] = [
  {
    src: "https://images.unsplash.com/photo-1769921546096-7a648d953a3e?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "urban exploration",
  },
  {
    src: "https://images.unsplash.com/photo-1777726515600-65be20641e1b?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "night scene",
  },
  {
    src: "https://images.unsplash.com/photo-1776582929657-9710d9cfa46a?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "yellow wildflowers",
  },
  {
    src: "https://images.unsplash.com/photo-1776582929656-78ad8b515d75?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "street with mount fuji",
  },
  {
    src: "https://images.unsplash.com/photo-1775990630948-3c1f696f4ab1?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "bridgestone bicycle shop",
  },
  {
    src: "https://images.unsplash.com/photo-1775380744191-8fbff371c40b?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "train window view",
  },
  {
    src: "https://images.unsplash.com/photo-1774775479879-082fd47d41e1?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "train tracks",
  },
  {
    src: "https://images.unsplash.com/photo-1773544517453-95c148cb42b7?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "lawson convenience store",
  },
  {
    src: "https://images.unsplash.com/photo-1771385809377-9b0348e1f8dc?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "street scene",
  },
  {
    src: "https://images.unsplash.com/photo-1775990631076-f6f208079475?q=80&w=500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    title: "japanese culture",
  },
];

const AuthCarousel: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState<number>(3);

  const toPrev = () => setActiveIndex((prev) => Math.max(0, prev - 1));
  const toNext = () =>
    setActiveIndex((prev) => Math.min(ASSETS.length - 1, prev + 1));
  const toSlide = (index: number) => setActiveIndex(index);
 
  const navigate = useNavigate();
  const goLogin = () => {
    navigate("/login");
  };



  return (
    <div className="carousel-root">
         <button 
          onClick={goLogin}
          style={{
                  position: "absolute",
                  top: "4%",
                  right: "5%",
                  zIndex: 10,

                  width: "80px",
                  height: "30px",
                  borderRadius: "999px",

                  color: "#fff",
                  background: "rgba(255, 255, 255, 0.22)",
                  backdropFilter: "blur(12px)",
                  WebkitBackdropFilter: "blur(12px)",

                  border: "1px solid rgba(255, 255, 255, 0.35)",
                  boxShadow: "0 8px 24px rgba(0, 0, 0, 0.16)",

                  cursor: "pointer",
                }}
        >
          Login
        </button>
      <div className="carousel-wrapper">
     
        <motion.div
          className="slides-track"
          animate={{ x: `${-activeIndex * (100 / ASSETS.length)}%` }}
          transition={{ type: "spring", bounce: 0.2, duration: 0.8 }}
        >
          {ASSETS.map((item, i) => {
            const isActive = activeIndex === i;
            return (
              <div className="slide-container" key={i}>
                <motion.div
                  className="slide-card"
                    animate={{
                    rotateY: (activeIndex - i) * 55,
                    scale: isActive ? 1 : 0.85,
                    opacity: Math.abs(activeIndex - i) > 3 ? 0 : 1,
                    }}
                  transition={{
                    type: "spring",
                    bounce: 0.1,
                    duration: 1,
                  }}
                >
                  <img
                    src={item.src}
                    alt={item.title}
                    className="slide-image"
                    onClick={() => toSlide(i)}
                  />
                  <motion.div
                    className="slide-title"
                    animate={{
                      filter: isActive ? "blur(0)" : "blur(2px)",
                      opacity: isActive ? 1 : 0,
                    }}
                  >
                    {item.title}
                  </motion.div>
                </motion.div>
              </div>
            );
          })}
        </motion.div>
      </div>

      <div className="controls">
        <button onClick={toPrev} className="ctrl-btn">
          <ChevronLeft />
        </button>
        <div className="dots">
          {ASSETS.map((_, i) => (
            <div
              key={i}
              onClick={() => toSlide(i)}
              className={`dot ${activeIndex === i ? "active" : ""}`}
            />
          ))}
        </div>
        <button onClick={toNext} className="ctrl-btn">
          <ChevronRight />
        </button>
      </div>
    </div>
  );
};

export default AuthCarousel;