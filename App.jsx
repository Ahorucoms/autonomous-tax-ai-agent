import { useState } from 'react'
import { Calculator, FileText, Info, DollarSign, Building, Users, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import './App.css'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Form states for different calculators
  const [incomeTaxForm, setIncomeTaxForm] = useState({
    annual_income: '',
    marital_status: 'single'
  })

  const [corporateTaxForm, setCorporateTaxForm] = useState({
    annual_profit: ''
  })

  const [vatForm, setVatForm] = useState({
    amount: '',
    vat_type: 'standard'
  })

  const [socialSecurityForm, setSocialSecurityForm] = useState({
    type: 'employee',
    weekly_wage: '',
    annual_income: '',
    birth_year: '1990'
  })

  const [stampDutyForm, setStampDutyForm] = useState({
    property_value: '',
    is_first_time_buyer: false,
    is_primary_residence: false
  })

  const calculateTax = async (endpoint, data) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await fetch(`/api/tax/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Calculation failed')
      }

      const result = await response.json()
      setResults(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleIncomeTaxCalculation = () => {
    calculateTax('calculate/income-tax', {
      annual_income: parseFloat(incomeTaxForm.annual_income),
      marital_status: incomeTaxForm.marital_status
    })
  }

  const handleCorporateTaxCalculation = () => {
    calculateTax('calculate/corporate-tax', {
      annual_profit: parseFloat(corporateTaxForm.annual_profit)
    })
  }

  const handleVatCalculation = () => {
    calculateTax('calculate/vat', {
      amount: parseFloat(vatForm.amount),
      vat_type: vatForm.vat_type
    })
  }

  const handleSocialSecurityCalculation = () => {
    if (socialSecurityForm.type === 'employee') {
      calculateTax('calculate/social-security/employee', {
        weekly_wage: parseFloat(socialSecurityForm.weekly_wage),
        birth_year: parseInt(socialSecurityForm.birth_year)
      })
    } else {
      calculateTax('calculate/social-security/self-employed', {
        annual_income: parseFloat(socialSecurityForm.annual_income),
        birth_year: parseInt(socialSecurityForm.birth_year)
      })
    }
  }

  const handleStampDutyCalculation = () => {
    calculateTax('calculate/stamp-duty', {
      property_value: parseFloat(stampDutyForm.property_value),
      is_first_time_buyer: stampDutyForm.is_first_time_buyer,
      is_primary_residence: stampDutyForm.is_primary_residence
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Malta AI Tax Agent
          </h1>
          <p className="text-lg text-gray-600">
            Your intelligent assistant for Malta tax calculations and compliance
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          <Tabs defaultValue="income-tax" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="income-tax" className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                Income Tax
              </TabsTrigger>
              <TabsTrigger value="corporate-tax" className="flex items-center gap-2">
                <Building className="w-4 h-4" />
                Corporate Tax
              </TabsTrigger>
              <TabsTrigger value="vat" className="flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                VAT
              </TabsTrigger>
              <TabsTrigger value="social-security" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Social Security
              </TabsTrigger>
              <TabsTrigger value="stamp-duty" className="flex items-center gap-2">
                <Home className="w-4 h-4" />
                Stamp Duty
              </TabsTrigger>
            </TabsList>

            {/* Income Tax Calculator */}
            <TabsContent value="income-tax">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Individual Income Tax Calculator
                  </CardTitle>
                  <CardDescription>
                    Calculate your personal income tax based on Malta's progressive tax system
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="annual-income">Annual Income (EUR)</Label>
                      <Input
                        id="annual-income"
                        type="number"
                        placeholder="Enter your annual income"
                        value={incomeTaxForm.annual_income}
                        onChange={(e) => setIncomeTaxForm({...incomeTaxForm, annual_income: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="marital-status">Marital Status</Label>
                      <Select value={incomeTaxForm.marital_status} onValueChange={(value) => setIncomeTaxForm({...incomeTaxForm, marital_status: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select marital status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="single">Single</SelectItem>
                          <SelectItem value="married">Married</SelectItem>
                          <SelectItem value="parental">Parental</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button onClick={handleIncomeTaxCalculation} disabled={loading} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate Income Tax
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Corporate Tax Calculator */}
            <TabsContent value="corporate-tax">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building className="w-5 h-5" />
                    Corporate Income Tax Calculator
                  </CardTitle>
                  <CardDescription>
                    Calculate corporate income tax at Malta's flat rate of 35%
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="annual-profit">Annual Profit (EUR)</Label>
                    <Input
                      id="annual-profit"
                      type="number"
                      placeholder="Enter annual taxable profit"
                      value={corporateTaxForm.annual_profit}
                      onChange={(e) => setCorporateTaxForm({...corporateTaxForm, annual_profit: e.target.value})}
                    />
                  </div>
                  <Button onClick={handleCorporateTaxCalculation} disabled={loading} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate Corporate Tax
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* VAT Calculator */}
            <TabsContent value="vat">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="w-5 h-5" />
                    VAT Calculator
                  </CardTitle>
                  <CardDescription>
                    Calculate VAT based on Malta's VAT rates
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="vat-amount">Net Amount (EUR)</Label>
                      <Input
                        id="vat-amount"
                        type="number"
                        placeholder="Enter net amount"
                        value={vatForm.amount}
                        onChange={(e) => setVatForm({...vatForm, amount: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="vat-type">VAT Rate</Label>
                      <Select value={vatForm.vat_type} onValueChange={(value) => setVatForm({...vatForm, vat_type: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select VAT rate" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="standard">Standard (18%)</SelectItem>
                          <SelectItem value="reduced_12">Reduced (12%)</SelectItem>
                          <SelectItem value="reduced_7">Reduced (7%)</SelectItem>
                          <SelectItem value="reduced_5">Reduced (5%)</SelectItem>
                          <SelectItem value="zero">Zero (0%)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button onClick={handleVatCalculation} disabled={loading} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate VAT
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Social Security Calculator */}
            <TabsContent value="social-security">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Social Security Contributions Calculator
                  </CardTitle>
                  <CardDescription>
                    Calculate Class 1 (Employee) or Class 2 (Self-Employed) contributions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="ss-type">Contribution Type</Label>
                    <Select value={socialSecurityForm.type} onValueChange={(value) => setSocialSecurityForm({...socialSecurityForm, type: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select contribution type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="employee">Class 1 (Employee)</SelectItem>
                        <SelectItem value="self-employed">Class 2 (Self-Employed)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {socialSecurityForm.type === 'employee' ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="weekly-wage">Weekly Wage (EUR)</Label>
                        <Input
                          id="weekly-wage"
                          type="number"
                          placeholder="Enter weekly wage"
                          value={socialSecurityForm.weekly_wage}
                          onChange={(e) => setSocialSecurityForm({...socialSecurityForm, weekly_wage: e.target.value})}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="birth-year">Birth Year</Label>
                        <Input
                          id="birth-year"
                          type="number"
                          placeholder="Enter birth year"
                          value={socialSecurityForm.birth_year}
                          onChange={(e) => setSocialSecurityForm({...socialSecurityForm, birth_year: e.target.value})}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="annual-income-ss">Annual Income (EUR)</Label>
                        <Input
                          id="annual-income-ss"
                          type="number"
                          placeholder="Enter annual income"
                          value={socialSecurityForm.annual_income}
                          onChange={(e) => setSocialSecurityForm({...socialSecurityForm, annual_income: e.target.value})}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="birth-year-se">Birth Year</Label>
                        <Input
                          id="birth-year-se"
                          type="number"
                          placeholder="Enter birth year"
                          value={socialSecurityForm.birth_year}
                          onChange={(e) => setSocialSecurityForm({...socialSecurityForm, birth_year: e.target.value})}
                        />
                      </div>
                    </div>
                  )}
                  
                  <Button onClick={handleSocialSecurityCalculation} disabled={loading} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate Social Security
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Stamp Duty Calculator */}
            <TabsContent value="stamp-duty">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Home className="w-5 h-5" />
                    Stamp Duty Calculator
                  </CardTitle>
                  <CardDescription>
                    Calculate stamp duty on property transfers in Malta
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="property-value">Property Value (EUR)</Label>
                    <Input
                      id="property-value"
                      type="number"
                      placeholder="Enter property transfer value"
                      value={stampDutyForm.property_value}
                      onChange={(e) => setStampDutyForm({...stampDutyForm, property_value: e.target.value})}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="first-time-buyer"
                      checked={stampDutyForm.is_first_time_buyer}
                      onCheckedChange={(checked) => setStampDutyForm({...stampDutyForm, is_first_time_buyer: checked})}
                    />
                    <Label htmlFor="first-time-buyer">First-time buyer</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="primary-residence"
                      checked={stampDutyForm.is_primary_residence}
                      onCheckedChange={(checked) => setStampDutyForm({...stampDutyForm, is_primary_residence: checked})}
                    />
                    <Label htmlFor="primary-residence">Primary residence</Label>
                  </div>
                  
                  <Button onClick={handleStampDutyCalculation} disabled={loading} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate Stamp Duty
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Results Section */}
          {(results || error) && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  Calculation Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-medium">Error: {error}</p>
                  </div>
                )}
                
                {results && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <pre className="text-sm text-green-800 whitespace-pre-wrap">
                      {JSON.stringify(results, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {loading && (
            <Card className="mt-6">
              <CardContent className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2">Calculating...</span>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

