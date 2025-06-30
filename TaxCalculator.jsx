import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Calculator, 
  TrendingUp, 
  PieChart, 
  FileText, 
  Download,
  Info,
  DollarSign,
  Percent
} from 'lucide-react';

export function TaxCalculator({ jurisdiction, language, persona }) {
  const [calculationType, setCalculationType] = useState('income');
  const [formData, setFormData] = useState({
    income: '',
    maritalStatus: 'single',
    dependents: '0',
    businessExpenses: '',
    vatAmount: '',
    vatRate: '18',
    propertyValue: '',
    isFirstTimeBuyer: false
  });
  const [results, setResults] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const calculationTypes = [
    { id: 'income', name: 'Income Tax', icon: DollarSign },
    { id: 'vat', name: 'VAT', icon: Percent },
    { id: 'corporate', name: 'Corporate Tax', icon: TrendingUp },
    { id: 'property', name: 'Property Tax', icon: FileText }
  ];

  const vatRates = {
    MT: [
      { rate: '18', label: '18% (Standard)' },
      { rate: '7', label: '7% (Reduced)' },
      { rate: '5', label: '5% (Super Reduced)' },
      { rate: '0', label: '0% (Zero Rate)' }
    ],
    FR: [
      { rate: '20', label: '20% (Standard)' },
      { rate: '10', label: '10% (Reduced)' },
      { rate: '5.5', label: '5.5% (Super Reduced)' },
      { rate: '2.1', label: '2.1% (Special)' }
    ]
  };

  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateTax = async () => {
    setIsCalculating(true);
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      let calculationResults;
      
      switch (calculationType) {
        case 'income':
          calculationResults = calculateIncomeTax();
          break;
        case 'vat':
          calculationResults = calculateVAT();
          break;
        case 'corporate':
          calculationResults = calculateCorporateTax();
          break;
        case 'property':
          calculationResults = calculatePropertyTax();
          break;
        default:
          calculationResults = { error: 'Invalid calculation type' };
      }
      
      setResults(calculationResults);
      
    } catch (error) {
      console.error('Calculation error:', error);
      setResults({ error: 'Calculation failed. Please try again.' });
    } finally {
      setIsCalculating(false);
    }
  };

  const calculateIncomeTax = () => {
    const income = parseFloat(formData.income) || 0;
    const dependents = parseInt(formData.dependents) || 0;
    const isMarried = formData.maritalStatus === 'married';
    
    if (jurisdiction === 'MT') {
      return calculateMaltaIncomeTax(income, isMarried, dependents);
    } else if (jurisdiction === 'FR') {
      return calculateFranceIncomeTax(income, isMarried, dependents);
    } else {
      return calculateGenericIncomeTax(income, isMarried, dependents);
    }
  };

  const calculateMaltaIncomeTax = (income, isMarried, dependents) => {
    const brackets = [
      { min: 0, max: 9100, rate: 0 },
      { min: 9101, max: 14500, rate: 15 },
      { min: 14501, max: 19500, rate: 25 },
      { min: 19501, max: 60000, rate: 25 },
      { min: 60001, max: Infinity, rate: 35 }
    ];

    let tax = 0;
    let breakdown = [];

    for (const bracket of brackets) {
      if (income > bracket.min) {
        const taxableInThisBracket = Math.min(income, bracket.max) - bracket.min + 1;
        const taxForBracket = taxableInThisBracket * (bracket.rate / 100);
        tax += taxForBracket;
        
        if (taxableInThisBracket > 0) {
          breakdown.push({
            range: `€${bracket.min.toLocaleString()} - €${bracket.max === Infinity ? '∞' : bracket.max.toLocaleString()}`,
            rate: `${bracket.rate}%`,
            taxableAmount: taxableInThisBracket,
            tax: taxForBracket
          });
        }
      }
    }

    // Apply allowances
    let allowances = 0;
    if (isMarried) allowances += 600;
    allowances += dependents * 300;

    const finalTax = Math.max(0, tax - allowances);
    const effectiveRate = income > 0 ? (finalTax / income) * 100 : 0;

    return {
      grossIncome: income,
      totalTax: finalTax,
      netIncome: income - finalTax,
      effectiveRate: effectiveRate,
      marginalRate: getMarginalRate(income, brackets),
      allowances: allowances,
      breakdown: breakdown,
      jurisdiction: 'Malta',
      currency: 'EUR'
    };
  };

  const calculateFranceIncomeTax = (income, isMarried, dependents) => {
    const brackets = [
      { min: 0, max: 10777, rate: 0 },
      { min: 10778, max: 27478, rate: 11 },
      { min: 27479, max: 78570, rate: 30 },
      { min: 78571, max: 168994, rate: 41 },
      { min: 168995, max: Infinity, rate: 45 }
    ];

    // Calculate quotient familial
    let parts = 1;
    if (isMarried) parts = 2;
    parts += dependents * 0.5;

    const quotientIncome = income / parts;
    
    let tax = 0;
    let breakdown = [];

    for (const bracket of brackets) {
      if (quotientIncome > bracket.min) {
        const taxableInThisBracket = Math.min(quotientIncome, bracket.max) - bracket.min + 1;
        const taxForBracket = taxableInThisBracket * (bracket.rate / 100);
        tax += taxForBracket;
        
        if (taxableInThisBracket > 0) {
          breakdown.push({
            range: `€${bracket.min.toLocaleString()} - €${bracket.max === Infinity ? '∞' : bracket.max.toLocaleString()}`,
            rate: `${bracket.rate}%`,
            taxableAmount: taxableInThisBracket,
            tax: taxForBracket
          });
        }
      }
    }

    const finalTax = tax * parts;
    const effectiveRate = income > 0 ? (finalTax / income) * 100 : 0;

    return {
      grossIncome: income,
      totalTax: finalTax,
      netIncome: income - finalTax,
      effectiveRate: effectiveRate,
      marginalRate: getMarginalRate(quotientIncome, brackets),
      quotientFamilial: parts,
      breakdown: breakdown,
      jurisdiction: 'France',
      currency: 'EUR'
    };
  };

  const calculateGenericIncomeTax = (income, isMarried, dependents) => {
    // Generic progressive tax calculation
    const rate = income <= 50000 ? 20 : income <= 100000 ? 30 : 40;
    const tax = income * (rate / 100);
    const allowances = (isMarried ? 2000 : 1000) + (dependents * 500);
    const finalTax = Math.max(0, tax - allowances);

    return {
      grossIncome: income,
      totalTax: finalTax,
      netIncome: income - finalTax,
      effectiveRate: income > 0 ? (finalTax / income) * 100 : 0,
      marginalRate: rate,
      allowances: allowances,
      jurisdiction: jurisdiction,
      currency: 'EUR'
    };
  };

  const calculateVAT = () => {
    const amount = parseFloat(formData.vatAmount) || 0;
    const rate = parseFloat(formData.vatRate) || 0;
    
    const vatAmount = amount * (rate / 100);
    const totalWithVAT = amount + vatAmount;

    return {
      netAmount: amount,
      vatRate: rate,
      vatAmount: vatAmount,
      totalAmount: totalWithVAT,
      jurisdiction: jurisdiction,
      currency: 'EUR'
    };
  };

  const calculateCorporateTax = () => {
    const profit = parseFloat(formData.income) || 0;
    const expenses = parseFloat(formData.businessExpenses) || 0;
    const taxableProfit = Math.max(0, profit - expenses);
    
    let rate;
    if (jurisdiction === 'MT') {
      rate = 35; // Malta corporate tax rate
    } else if (jurisdiction === 'FR') {
      rate = taxableProfit <= 42500 ? 15 : 25; // France reduced rate for small businesses
    } else {
      rate = 25; // Generic rate
    }

    const tax = taxableProfit * (rate / 100);

    return {
      grossProfit: profit,
      businessExpenses: expenses,
      taxableProfit: taxableProfit,
      corporateTaxRate: rate,
      corporateTax: tax,
      netProfit: taxableProfit - tax,
      jurisdiction: jurisdiction,
      currency: 'EUR'
    };
  };

  const calculatePropertyTax = () => {
    const value = parseFloat(formData.propertyValue) || 0;
    
    let rate;
    if (jurisdiction === 'MT') {
      rate = formData.isFirstTimeBuyer ? 0 : 5; // Malta stamp duty
    } else {
      rate = 3; // Generic property tax rate
    }

    const tax = value * (rate / 100);

    return {
      propertyValue: value,
      taxRate: rate,
      propertyTax: tax,
      isFirstTimeBuyer: formData.isFirstTimeBuyer,
      jurisdiction: jurisdiction,
      currency: 'EUR'
    };
  };

  const getMarginalRate = (income, brackets) => {
    for (const bracket of brackets) {
      if (income >= bracket.min && income <= bracket.max) {
        return bracket.rate;
      }
    }
    return brackets[brackets.length - 1].rate;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EU', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const exportResults = () => {
    if (!results) return;
    
    const data = {
      calculation_type: calculationType,
      jurisdiction: jurisdiction,
      language: language,
      persona: persona?.name,
      input_data: formData,
      results: results,
      calculated_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tax-calculation-${calculationType}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Tax Calculator</h1>
        <p className="text-xl text-muted-foreground mb-4">
          Calculate taxes for {jurisdiction} with precision and accuracy
        </p>
        <div className="flex items-center justify-center space-x-2">
          <Badge variant="secondary">{jurisdiction}</Badge>
          <Badge variant="outline">{language.toUpperCase()}</Badge>
          {persona && <Badge variant="default">{persona.name}</Badge>}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculator Selection */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calculator className="h-5 w-5" />
                <span>Calculator Type</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {calculationTypes.map(type => {
                  const IconComponent = type.icon;
                  return (
                    <Button
                      key={type.id}
                      variant={calculationType === type.id ? "default" : "outline"}
                      className="w-full justify-start"
                      onClick={() => setCalculationType(type.id)}
                    >
                      <IconComponent className="h-4 w-4 mr-2" />
                      {type.name}
                    </Button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Input Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>
                {calculationTypes.find(t => t.id === calculationType)?.name} Calculator
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Income Tax Form */}
                {calculationType === 'income' && (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="income">Annual Income (€)</Label>
                      <Input
                        id="income"
                        type="number"
                        value={formData.income}
                        onChange={(e) => updateFormData('income', e.target.value)}
                        placeholder="Enter your annual income"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="maritalStatus">Marital Status</Label>
                        <Select value={formData.maritalStatus} onValueChange={(value) => updateFormData('maritalStatus', value)}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="single">Single</SelectItem>
                            <SelectItem value="married">Married</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="dependents">Number of Dependents</Label>
                        <Input
                          id="dependents"
                          type="number"
                          value={formData.dependents}
                          onChange={(e) => updateFormData('dependents', e.target.value)}
                          min="0"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* VAT Form */}
                {calculationType === 'vat' && (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="vatAmount">Net Amount (€)</Label>
                      <Input
                        id="vatAmount"
                        type="number"
                        value={formData.vatAmount}
                        onChange={(e) => updateFormData('vatAmount', e.target.value)}
                        placeholder="Enter net amount"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="vatRate">VAT Rate</Label>
                      <Select value={formData.vatRate} onValueChange={(value) => updateFormData('vatRate', value)}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {(vatRates[jurisdiction] || vatRates.MT).map(rate => (
                            <SelectItem key={rate.rate} value={rate.rate}>
                              {rate.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}

                {/* Corporate Tax Form */}
                {calculationType === 'corporate' && (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="profit">Annual Profit (€)</Label>
                      <Input
                        id="profit"
                        type="number"
                        value={formData.income}
                        onChange={(e) => updateFormData('income', e.target.value)}
                        placeholder="Enter annual profit"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="businessExpenses">Business Expenses (€)</Label>
                      <Input
                        id="businessExpenses"
                        type="number"
                        value={formData.businessExpenses}
                        onChange={(e) => updateFormData('businessExpenses', e.target.value)}
                        placeholder="Enter deductible expenses"
                      />
                    </div>
                  </div>
                )}

                {/* Property Tax Form */}
                {calculationType === 'property' && (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="propertyValue">Property Value (€)</Label>
                      <Input
                        id="propertyValue"
                        type="number"
                        value={formData.propertyValue}
                        onChange={(e) => updateFormData('propertyValue', e.target.value)}
                        placeholder="Enter property value"
                      />
                    </div>
                    
                    {jurisdiction === 'MT' && (
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="firstTimeBuyer"
                          checked={formData.isFirstTimeBuyer}
                          onChange={(e) => updateFormData('isFirstTimeBuyer', e.target.checked)}
                        />
                        <Label htmlFor="firstTimeBuyer">First-time buyer</Label>
                      </div>
                    )}
                  </div>
                )}

                <Button 
                  onClick={calculateTax} 
                  disabled={isCalculating}
                  className="w-full"
                  size="lg"
                >
                  {isCalculating ? 'Calculating...' : 'Calculate Tax'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Results */}
      {results && !results.error && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <PieChart className="h-5 w-5" />
                <span>Calculation Results</span>
              </CardTitle>
              <Button variant="outline" size="sm" onClick={exportResults}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="breakdown">Breakdown</TabsTrigger>
              </TabsList>
              
              <TabsContent value="summary" className="space-y-4">
                {calculationType === 'income' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {formatCurrency(results.netIncome)}
                          </div>
                          <p className="text-sm text-muted-foreground">Net Income</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">
                            {formatCurrency(results.totalTax)}
                          </div>
                          <p className="text-sm text-muted-foreground">Total Tax</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {results.effectiveRate.toFixed(1)}%
                          </div>
                          <p className="text-sm text-muted-foreground">Effective Rate</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {calculationType === 'vat' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {formatCurrency(results.netAmount)}
                          </div>
                          <p className="text-sm text-muted-foreground">Net Amount</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {formatCurrency(results.vatAmount)}
                          </div>
                          <p className="text-sm text-muted-foreground">VAT ({results.vatRate}%)</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {formatCurrency(results.totalAmount)}
                          </div>
                          <p className="text-sm text-muted-foreground">Total Amount</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {calculationType === 'corporate' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {formatCurrency(results.taxableProfit)}
                          </div>
                          <p className="text-sm text-muted-foreground">Taxable Profit</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">
                            {formatCurrency(results.corporateTax)}
                          </div>
                          <p className="text-sm text-muted-foreground">Corporate Tax ({results.corporateTaxRate}%)</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {formatCurrency(results.netProfit)}
                          </div>
                          <p className="text-sm text-muted-foreground">Net Profit</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {calculationType === 'property' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {formatCurrency(results.propertyValue)}
                          </div>
                          <p className="text-sm text-muted-foreground">Property Value</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {formatCurrency(results.propertyTax)}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Property Tax ({results.taxRate}%)
                            {results.isFirstTimeBuyer && ' - First Time Buyer'}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="breakdown" className="space-y-4">
                {results.breakdown && (
                  <div className="space-y-2">
                    <h4 className="font-medium">Tax Bracket Breakdown</h4>
                    {results.breakdown.map((bracket, index) => (
                      <div key={index} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                        <div>
                          <span className="font-medium">{bracket.range}</span>
                          <span className="text-muted-foreground ml-2">({bracket.rate})</span>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">{formatCurrency(bracket.tax)}</div>
                          <div className="text-sm text-muted-foreground">
                            on {formatCurrency(bracket.taxableAmount)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {results.allowances && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Allowances & Deductions</h4>
                    <div className="p-3 bg-green-50 rounded-lg">
                      <div className="flex justify-between">
                        <span>Total Allowances</span>
                        <span className="font-medium text-green-600">
                          -{formatCurrency(results.allowances)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {results?.error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{results.error}</AlertDescription>
        </Alert>
      )}

      {/* Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="h-5 w-5" />
            <span>Important Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              These calculations are estimates based on current tax rates for {jurisdiction}. 
              Actual tax liability may vary based on individual circumstances, deductions, and other factors. 
              Please consult with a qualified tax professional for personalized advice.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}

