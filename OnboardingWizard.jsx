import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronLeft, Globe, User, MessageCircle, Mail, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'

const OnboardingWizard = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    jurisdiction: 'malta',
    authMethod: '',
    userType: '',
    name: '',
    email: '',
    phone: '',
    taxId: '',
    language: 'en',
    acceptTerms: false,
    acceptPrivacy: false
  })
  const [showDemo, setShowDemo] = useState(false)

  const jurisdictions = [
    { value: 'malta', label: 'Malta', flag: '🇲🇹' },
    { value: 'cyprus', label: 'Cyprus', flag: '🇨🇾' },
    { value: 'ireland', label: 'Ireland', flag: '🇮🇪' },
    { value: 'luxembourg', label: 'Luxembourg', flag: '🇱🇺' }
  ]

  const userTypes = [
    { value: 'individual', label: 'Individual Taxpayer', description: 'Personal income tax and returns' },
    { value: 'business', label: 'Business Owner', description: 'Corporate tax, VAT, and payroll' },
    { value: 'advisor', label: 'Tax Advisor/Accountant', description: 'Multi-client management' },
    { value: 'vsp', label: 'Virtual Service Provider', description: 'AML/KYC compliance' }
  ]

  const steps = [
    {
      title: 'Choose Your Jurisdiction',
      description: 'Select your primary tax jurisdiction',
      component: JurisdictionStep
    },
    {
      title: 'How Would You Like to Start?',
      description: 'Choose your preferred access method',
      component: AuthMethodStep
    },
    {
      title: 'Tell Us About Yourself',
      description: 'Help us personalize your experience',
      component: UserTypeStep
    },
    {
      title: 'Account Details',
      description: 'Create your secure account',
      component: AccountDetailsStep
    },
    {
      title: 'Terms & Privacy',
      description: 'Review and accept our terms',
      component: TermsStep
    }
  ]

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      onComplete(formData)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 0: return formData.jurisdiction
      case 1: return formData.authMethod || showDemo
      case 2: return formData.userType
      case 3: return formData.name && (formData.email || formData.phone)
      case 4: return formData.acceptTerms && formData.acceptPrivacy
      default: return true
    }
  }

  function JurisdictionStep() {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4">
          {jurisdictions.map((jurisdiction) => (
            <motion.div
              key={jurisdiction.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card 
                className={`cursor-pointer transition-all min-h-[44px] ${
                  formData.jurisdiction === jurisdiction.value 
                    ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => setFormData({...formData, jurisdiction: jurisdiction.value})}
              >
                <CardContent className="flex items-center p-4">
                  <span className="text-2xl mr-3">{jurisdiction.flag}</span>
                  <div>
                    <h3 className="font-semibold">{jurisdiction.label}</h3>
                    <p className="text-sm text-muted-foreground">Tax jurisdiction</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  function AuthMethodStep() {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card 
              className={`cursor-pointer transition-all min-h-[44px] ${
                showDemo ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-950' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
              onClick={() => {
                setShowDemo(true)
                setFormData({...formData, authMethod: 'demo'})
              }}
            >
              <CardContent className="flex items-center p-4">
                <Eye className="w-6 h-6 mr-3 text-green-600" />
                <div>
                  <h3 className="font-semibold">Explore Anonymously</h3>
                  <p className="text-sm text-muted-foreground">Try the demo without creating an account</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card 
              className={`cursor-pointer transition-all min-h-[44px] ${
                formData.authMethod === 'whatsapp' ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
              onClick={() => {
                setShowDemo(false)
                setFormData({...formData, authMethod: 'whatsapp'})
              }}
            >
              <CardContent className="flex items-center p-4">
                <MessageCircle className="w-6 h-6 mr-3 text-green-600" />
                <div>
                  <h3 className="font-semibold">WhatsApp Login</h3>
                  <p className="text-sm text-muted-foreground">Quick verification via WhatsApp OTP</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card 
              className={`cursor-pointer transition-all min-h-[44px] ${
                formData.authMethod === 'email' ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
              onClick={() => {
                setShowDemo(false)
                setFormData({...formData, authMethod: 'email'})
              }}
            >
              <CardContent className="flex items-center p-4">
                <Mail className="w-6 h-6 mr-3 text-blue-600" />
                <div>
                  <h3 className="font-semibold">Email Login</h3>
                  <p className="text-sm text-muted-foreground">Traditional email with magic link</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {showDemo && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="bg-green-50 dark:bg-green-950 p-4 rounded-lg border border-green-200 dark:border-green-800"
          >
            <p className="text-sm text-green-800 dark:text-green-200">
              <strong>Demo Mode:</strong> You can explore all features anonymously. 
              You'll be prompted to create an account only when submitting actual tax filings.
            </p>
          </motion.div>
        )}
      </div>
    )
  }

  function UserTypeStep() {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4">
          {userTypes.map((type) => (
            <motion.div
              key={type.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card 
                className={`cursor-pointer transition-all min-h-[44px] ${
                  formData.userType === type.value 
                    ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => setFormData({...formData, userType: type.value})}
              >
                <CardContent className="p-4">
                  <h3 className="font-semibold mb-1">{type.label}</h3>
                  <p className="text-sm text-muted-foreground">{type.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  function AccountDetailsStep() {
    if (showDemo) {
      return (
        <div className="text-center py-8">
          <EyeOff className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Demo Mode Active</h3>
          <p className="text-muted-foreground">
            You're exploring anonymously. Account creation will be prompted when needed for actual filings.
          </p>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="name">Full Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Enter your full name"
              className="min-h-[44px]"
            />
          </div>

          {formData.authMethod === 'email' && (
            <div>
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="Enter your email"
                className="min-h-[44px]"
              />
            </div>
          )}

          {formData.authMethod === 'whatsapp' && (
            <div>
              <Label htmlFor="phone">WhatsApp Number *</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                placeholder="+356 XXXX XXXX"
                className="min-h-[44px]"
              />
            </div>
          )}

          <div>
            <Label htmlFor="taxId">Tax ID (Optional)</Label>
            <Input
              id="taxId"
              value={formData.taxId}
              onChange={(e) => setFormData({...formData, taxId: e.target.value})}
              placeholder="Enter your tax identification number"
              className="min-h-[44px]"
            />
          </div>

          <div>
            <Label htmlFor="language">Preferred Language</Label>
            <Select value={formData.language} onValueChange={(value) => setFormData({...formData, language: value})}>
              <SelectTrigger className="min-h-[44px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="mt">Malti</SelectItem>
                <SelectItem value="fr">Français</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    )
  }

  function TermsStep() {
    if (showDemo) {
      return (
        <div className="text-center py-8">
          <h3 className="text-lg font-semibold mb-4">Ready to Explore!</h3>
          <p className="text-muted-foreground mb-6">
            You can now explore all features in demo mode. Terms and privacy policies will be presented when you're ready to create an account.
          </p>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <Checkbox
              id="terms"
              checked={formData.acceptTerms}
              onCheckedChange={(checked) => setFormData({...formData, acceptTerms: checked})}
              className="mt-1"
            />
            <div>
              <Label htmlFor="terms" className="text-sm">
                I accept the <a href="#" className="text-blue-600 hover:underline">Terms of Service</a>
              </Label>
              <p className="text-xs text-muted-foreground mt-1">
                Including MFSA compliance and audit requirements
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Checkbox
              id="privacy"
              checked={formData.acceptPrivacy}
              onCheckedChange={(checked) => setFormData({...formData, acceptPrivacy: checked})}
              className="mt-1"
            />
            <div>
              <Label htmlFor="privacy" className="text-sm">
                I accept the <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>
              </Label>
              <p className="text-xs text-muted-foreground mt-1">
                GDPR compliant data processing and 10-year retention
              </p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-sm mb-2">Data Protection Summary</h4>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>• End-to-end encryption for all sensitive data</li>
            <li>• Activity logs retained for 10 years (MFSA requirement)</li>
            <li>• GDPR delete-me flow available in settings</li>
            <li>• No data sharing with third parties without consent</li>
          </ul>
        </div>
      </div>
    )
  }

  const CurrentStepComponent = steps[currentStep].component

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-blue-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center mb-4">
            <Globe className="w-8 h-8 text-blue-600 mr-2" />
            <h1 className="text-2xl font-bold">Malta Tax AI</h1>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-4">
            <motion.div
              className="bg-blue-600 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          
          <CardTitle className="text-xl">{steps[currentStep].title}</CardTitle>
          <CardDescription>{steps[currentStep].description}</CardDescription>
        </CardHeader>

        <CardContent>
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <CurrentStepComponent />
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 0}
              className="min-h-[44px]"
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Back
            </Button>

            <Button
              onClick={nextStep}
              disabled={!canProceed()}
              className="min-h-[44px]"
            >
              {currentStep === steps.length - 1 ? 'Complete Setup' : 'Continue'}
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default OnboardingWizard

