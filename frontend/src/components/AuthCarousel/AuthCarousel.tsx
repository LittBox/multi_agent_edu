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
    src: "https://www.ynu.edu.cn/__local/9/1B/9A/9164431D754DC37494DB20A4770_9CB87F03_2315B.jpg",
    title: "紧跟政策",
  },
  {
    src: "https://www.ynu.edu.cn/images/2026biyegehui.jpg",
    title: "毕业歌会",
  },
  {
    src: "https://www.ynu.edu.cn/__local/7/46/C9/99AF9883CF0FB16330DE3C108BA_4F817D26_F862A.jpg",
    title: "校园马拉松",
  },
  {
    src: "https://www.ynu.edu.cn/images/biyedianlidatu.jpg",
    title: "毕业典礼",
  },
  {
    src: "https://www.ynu.edu.cn/images/fuchuandai-mingyuanloucaihong.jpg",
    title: "雨后彩虹",
  },
  {
    src: "https://www.ynu.edu.cn/images/wangzhen-chenggongquanjing2.jpg",
    title: "俯瞰云大",
  },
  {
    src: "https://www.ynu.edu.cn/images/tongxingyu-wuliguan.jpg",
    title: "东陆物理馆",
  },
  {
    src: "https://www.ynu.edu.cn/images/yinsijie-dongmenyundongchangzonghexunlianguan.jpg",
    title: "东门体育馆",
  },
  {
    src: "https://www.ynu.edu.cn/images/yunshanquanjing.jpg",
    title: "云山夜景",
  },
  {
    src: "https://www.ynu.edu.cn/__local/F/A0/8C/08F8C73167923DE34600D2D213A_1C1FBF7D_1E4FC0.jpg",
    title: "云山歌会",
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