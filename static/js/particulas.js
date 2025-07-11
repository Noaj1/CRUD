particlesJS('particles-js', {
  particles: {
      number: {
          value: 50, // Número de partículas
          density: { enable: true, value_area: 800 }
      },
      color: { value: "#ffffff" },
      shape: { type: "circle" },
      opacity: {
          value: 0.5,
          anim: { enable: false }
      },
      size: {
          value: 3,
          random: true,
          anim: { enable: false }
      },
      line_linked: {
          enable: true,
          distance: 150,
          color: "#ffffff",
          opacity: 0.4,
          width: 1
      },
      move: {
          enable: true,
          speed: 4,
          direction: "none",
          random: false,
          straight: false,
          out_mode: "out",
          bounce: false
      }
  },
  interactivity: {
      detect_on: "canvas",
      events: {
          onhover: { enable: true, mode: "grab" },
          onclick: { enable: true, mode: "push" },
          resize: true
      },
      modes: {
          grab: { distance: 140, line_linked: { opacity: 1 } },
          bubble: { distance: 200, size: 40, duration: 2, opacity: 0.8 },
          repulse: { distance: 200, duration: 0.4 },
          push: { particles_nb: 4 },
          remove: { particles_nb: 2 }
      }
  },
  retina_detect: true
});
