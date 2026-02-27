// Motion Design Constants - from medical-rag design system

const EASINGS = {
  smoothOut: [0, 0, 0.2, 1],
}

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
}

export const fadeInUp = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.25, ease: EASINGS.smoothOut },
  },
  exit: { opacity: 0, y: -4, transition: { duration: 0.15 } },
}

export const staggerContainer = (staggerDelay = 0.04, delayChildren = 0) => ({
  hidden: { opacity: 1 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren: delayChildren,
    },
  },
})

export const listItem = {
  hidden: { opacity: 0, y: 6 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, ease: EASINGS.smoothOut },
  },
}

export const userMessage = {
  hidden: { opacity: 0, x: 16, scale: 0.98 },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: { duration: 0.25, ease: EASINGS.smoothOut },
  },
}

export const assistantMessage = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.25, ease: EASINGS.smoothOut },
  },
}

export const buttonHover = {
  y: -1,
  transition: { duration: 0.15 },
}

export const buttonTap = {
  scale: 0.98,
  transition: { duration: 0.1 },
}
