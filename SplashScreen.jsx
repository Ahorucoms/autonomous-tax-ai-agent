import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bot, Shield, Globe, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'

const SplashScreen = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0)
  
  const features = [
    {
      icon: Bot,
      title: "AI-Powered",
      description: "Autonomous tax agent with GPT-4o reasoning"
    },
    {
      icon: Shield,
      title: "Regulation-Ready",
      description: "MFSA compliant with GDPR protection"
    },
    {
      icon: Globe,
      title: "Multi-Jurisdiction",
      description: "White-label ready for any country"
    },
    {
      icon: Zap,
      title: "Instant Filing",
      description: "End-to-end tax submission in seconds"
    }
  ]

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentStep < features.length - 1) {
        setCurrentStep(currentStep + 1)
      }
    }, 1500)
    
    return () => clearTimeout(timer)
  }, [currentStep, features.length])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 flex flex-col items-center justify-center p-6 text-white">
      {/* Logo and Title */}
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-12"
      >
        <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-6 mx-auto backdrop-blur-sm">
          <Bot className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold mb-2">Malta Tax AI</h1>
        <p className="text-blue-100 text-lg">Autonomous Tax Agent</p>
      </motion.div>

      {/* Features Showcase */}
      <div className="w-full max-w-md mb-12">
        {features.map((feature, index) => {
          const Icon = feature.icon
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -50 }}
              animate={{ 
                opacity: index <= currentStep ? 1 : 0.3,
                x: 0,
                scale: index === currentStep ? 1.05 : 1
              }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`flex items-center p-4 rounded-lg mb-4 ${
                index <= currentStep 
                  ? 'bg-white/20 backdrop-blur-sm' 
                  : 'bg-white/10'
              }`}
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-4 ${
                index <= currentStep ? 'bg-white/30' : 'bg-white/20'
              }`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">{feature.title}</h3>
                <p className="text-blue-100 text-sm">{feature.description}</p>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Progress Indicator */}
      <div className="flex space-x-2 mb-8">
        {features.map((_, index) => (
          <motion.div
            key={index}
            className={`w-3 h-3 rounded-full ${
              index <= currentStep ? 'bg-white' : 'bg-white/30'
            }`}
            animate={{
              scale: index === currentStep ? 1.2 : 1
            }}
            transition={{ duration: 0.3 }}
          />
        ))}
      </div>

      {/* Get Started Button */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 2 }}
      >
        <Button
          onClick={onComplete}
          size="lg"
          className="bg-white text-blue-700 hover:bg-blue-50 font-semibold px-8 py-3 text-lg min-h-[44px]"
        >
          Get Started
        </Button>
      </motion.div>

      {/* Footer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 2.5 }}
        className="text-blue-200 text-sm mt-8 text-center"
      >
        Production-grade • Regulation-ready • WCAG 2.2-AA
      </motion.p>
    </div>
  )
}

export default SplashScreen

