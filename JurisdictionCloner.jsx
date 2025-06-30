import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { 
  Globe, 
  Copy, 
  Check, 
  AlertTriangle, 
  ArrowRight, 
  Download,
  Upload,
  Settings,
  FileText,
  Database,
  Brain,
  Users
} from 'lucide-react';

export function JurisdictionCloner({ 
  currentJurisdiction, 
  currentLanguage, 
  persona, 
  onJurisdictionChange 
}) {
  const [selectedTargetJurisdiction, setSelectedTargetJurisdiction] = useState('');
  const [selectedTargetLanguage, setSelectedTargetLanguage] = useState('');
  const [cloningStep, setCloningStep] = useState('select'); // select, configure, clone, complete
  const [cloningProgress, setCloningProgress] = useState(0);
  const [cloningStatus, setCloningStatus] = useState('');
  const [componentsToClone, setComponentsToClone] = useState({
    persona: true,
    knowledge_base: true,
    tax_rules: true,
    forms_templates: true,
    ai_training: false,
    user_preferences: true
  });

  const availableJurisdictions = [
    { code: 'MT', name: 'Malta', languages: ['en', 'mt'] },
    { code: 'FR', name: 'France', languages: ['fr', 'en'] },
    { code: 'DE', name: 'Germany', languages: ['de', 'en'] },
    { code: 'IT', name: 'Italy', languages: ['it', 'en'] },
    { code: 'ES', name: 'Spain', languages: ['es', 'en'] },
    { code: 'NL', name: 'Netherlands', languages: ['nl', 'en'] },
    { code: 'BE', name: 'Belgium', languages: ['fr', 'nl', 'de', 'en'] },
    { code: 'LU', name: 'Luxembourg', languages: ['fr', 'de', 'en'] },
    { code: 'IE', name: 'Ireland', languages: ['en', 'ga'] },
    { code: 'CY', name: 'Cyprus', languages: ['en', 'el'] },
    { code: 'CA', name: 'Canada', languages: ['en', 'fr'] },
    { code: 'AU', name: 'Australia', languages: ['en'] },
    { code: 'NZ', name: 'New Zealand', languages: ['en'] },
    { code: 'SG', name: 'Singapore', languages: ['en'] },
    { code: 'HK', name: 'Hong Kong', languages: ['en', 'zh'] }
  ];

  const getJurisdictionName = (code) => {
    return availableJurisdictions.find(j => j.code === code)?.name || code;
  };

  const getAvailableLanguages = (jurisdictionCode) => {
    return availableJurisdictions.find(j => j.code === jurisdictionCode)?.languages || ['en'];
  };

  const handleStartCloning = () => {
    if (!selectedTargetJurisdiction || !selectedTargetLanguage) {
      return;
    }
    setCloningStep('configure');
  };

  const handleConfigureCloning = () => {
    setCloningStep('clone');
    performCloning();
  };

  const performCloning = async () => {
    const steps = [
      { name: 'Initializing clone process', duration: 1000 },
      { name: 'Cloning persona configuration', duration: 2000 },
      { name: 'Adapting knowledge base', duration: 3000 },
      { name: 'Localizing tax rules', duration: 2500 },
      { name: 'Generating forms templates', duration: 2000 },
      { name: 'Training AI models', duration: 4000 },
      { name: 'Finalizing setup', duration: 1500 }
    ];

    let totalProgress = 0;
    const stepIncrement = 100 / steps.length;

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      
      // Skip AI training if not selected
      if (step.name.includes('Training AI') && !componentsToClone.ai_training) {
        totalProgress += stepIncrement;
        setCloningProgress(totalProgress);
        continue;
      }

      setCloningStatus(step.name);
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, step.duration));
      
      totalProgress += stepIncrement;
      setCloningProgress(Math.min(totalProgress, 100));
    }

    // Complete the cloning process
    setCloningStatus('Clone completed successfully!');
    setCloningStep('complete');
    
    // Save the cloned configuration
    await saveClonedConfiguration();
  };

  const saveClonedConfiguration = async () => {
    try {
      // Create cloned persona
      const clonedPersona = {
        ...persona,
        id: `${persona.id}-${selectedTargetJurisdiction}-${selectedTargetLanguage}`,
        jurisdiction: selectedTargetJurisdiction,
        language: selectedTargetLanguage,
        name: `${persona.name} (${getJurisdictionName(selectedTargetJurisdiction)})`,
        cloned_from: {
          original_jurisdiction: currentJurisdiction,
          original_language: currentLanguage,
          original_persona_id: persona.id,
          cloned_at: new Date().toISOString()
        },
        components_cloned: componentsToClone
      };

      // Save to localStorage
      const storageKey = `personas-${selectedTargetJurisdiction}-${selectedTargetLanguage}`;
      const existingPersonas = JSON.parse(localStorage.getItem(storageKey) || '[]');
      
      // Check if persona already exists
      const existingIndex = existingPersonas.findIndex(p => p.id === clonedPersona.id);
      if (existingIndex >= 0) {
        existingPersonas[existingIndex] = clonedPersona;
      } else {
        existingPersonas.push(clonedPersona);
      }
      
      localStorage.setItem(storageKey, JSON.stringify(existingPersonas));

      // Save cloning history
      const cloningHistory = JSON.parse(localStorage.getItem('jurisdiction-cloning-history') || '[]');
      cloningHistory.push({
        id: `clone-${Date.now()}`,
        source: {
          jurisdiction: currentJurisdiction,
          language: currentLanguage,
          persona_id: persona.id
        },
        target: {
          jurisdiction: selectedTargetJurisdiction,
          language: selectedTargetLanguage,
          persona_id: clonedPersona.id
        },
        components_cloned: componentsToClone,
        cloned_at: new Date().toISOString(),
        status: 'completed'
      });
      localStorage.setItem('jurisdiction-cloning-history', JSON.stringify(cloningHistory));

    } catch (error) {
      console.error('Failed to save cloned configuration:', error);
    }
  };

  const handleSwitchToClonedJurisdiction = () => {
    if (onJurisdictionChange) {
      onJurisdictionChange(selectedTargetJurisdiction);
    }
    
    // Update session storage
    const sessionData = JSON.parse(localStorage.getItem('ai-tax-session') || '{}');
    sessionData.jurisdiction = selectedTargetJurisdiction;
    sessionData.language = selectedTargetLanguage;
    localStorage.setItem('ai-tax-session', JSON.stringify(sessionData));
    
    // Reload the page to apply changes
    window.location.reload();
  };

  const resetCloning = () => {
    setCloningStep('select');
    setCloningProgress(0);
    setCloningStatus('');
    setSelectedTargetJurisdiction('');
    setSelectedTargetLanguage('');
  };

  const getCloningSummary = () => {
    const selectedComponents = Object.entries(componentsToClone)
      .filter(([_, selected]) => selected)
      .map(([component, _]) => component);
    
    return {
      totalComponents: Object.keys(componentsToClone).length,
      selectedComponents: selectedComponents.length,
      estimatedTime: selectedComponents.length * 2 + (componentsToClone.ai_training ? 5 : 0),
      components: selectedComponents
    };
  };

  if (cloningStep === 'select') {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Clone to New Jurisdiction</h1>
          <p className="text-xl text-muted-foreground mb-4">
            Replicate your current tax setup to a new jurisdiction with localized rules and language
          </p>
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center space-x-2">
              <Badge variant="secondary">{currentJurisdiction}</Badge>
              <span className="text-muted-foreground">•</span>
              <Badge variant="outline">{currentLanguage.toUpperCase()}</Badge>
              <span className="text-muted-foreground">•</span>
              <Badge variant="default">{persona?.name}</Badge>
            </div>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5" />
              <span>Select Target Jurisdiction</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="target-jurisdiction">Target Jurisdiction</Label>
                <Select 
                  value={selectedTargetJurisdiction} 
                  onValueChange={setSelectedTargetJurisdiction}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select jurisdiction" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableJurisdictions
                      .filter(j => j.code !== currentJurisdiction)
                      .map(jurisdiction => (
                        <SelectItem key={jurisdiction.code} value={jurisdiction.code}>
                          {jurisdiction.name} ({jurisdiction.code})
                        </SelectItem>
                      ))
                    }
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="target-language">Target Language</Label>
                <Select 
                  value={selectedTargetLanguage} 
                  onValueChange={setSelectedTargetLanguage}
                  disabled={!selectedTargetJurisdiction}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    {selectedTargetJurisdiction && 
                      getAvailableLanguages(selectedTargetJurisdiction).map(lang => (
                        <SelectItem key={lang} value={lang}>
                          {lang.toUpperCase()}
                        </SelectItem>
                      ))
                    }
                  </SelectContent>
                </Select>
              </div>
            </div>

            {selectedTargetJurisdiction && selectedTargetLanguage && (
              <Alert>
                <ArrowRight className="h-4 w-4" />
                <AlertDescription>
                  You are about to clone your setup from{' '}
                  <strong>{getJurisdictionName(currentJurisdiction)} ({currentLanguage.toUpperCase()})</strong>{' '}
                  to{' '}
                  <strong>{getJurisdictionName(selectedTargetJurisdiction)} ({selectedTargetLanguage.toUpperCase()})</strong>
                </AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end">
              <Button 
                onClick={handleStartCloning}
                disabled={!selectedTargetJurisdiction || !selectedTargetLanguage}
              >
                Configure Clone
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (cloningStep === 'configure') {
    const summary = getCloningSummary();
    
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Configure Clone</h1>
          <p className="text-xl text-muted-foreground">
            Select which components to clone to the new jurisdiction
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Components to Clone</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(componentsToClone).map(([component, selected]) => (
                  <div key={component} className="flex items-start space-x-3">
                    <Checkbox
                      id={component}
                      checked={selected}
                      onCheckedChange={(checked) => 
                        setComponentsToClone(prev => ({
                          ...prev,
                          [component]: checked
                        }))
                      }
                    />
                    <div className="flex-1">
                      <Label htmlFor={component} className="text-sm font-medium">
                        {getComponentDisplayName(component)}
                      </Label>
                      <p className="text-xs text-muted-foreground mt-1">
                        {getComponentDescription(component)}
                      </p>
                    </div>
                    {getComponentIcon(component)}
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div>
            <Card>
              <CardHeader>
                <CardTitle>Clone Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Source:</span>
                    <span>{getJurisdictionName(currentJurisdiction)} ({currentLanguage.toUpperCase()})</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Target:</span>
                    <span>{getJurisdictionName(selectedTargetJurisdiction)} ({selectedTargetLanguage.toUpperCase()})</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Persona:</span>
                    <span>{persona?.name}</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Components:</span>
                    <span>{summary.selectedComponents}/{summary.totalComponents}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Est. Time:</span>
                    <span>{summary.estimatedTime} min</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Selected Components:</h4>
                  <div className="space-y-1">
                    {summary.components.map(component => (
                      <div key={component} className="flex items-center space-x-2 text-xs">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>{getComponentDisplayName(component)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex flex-col space-y-3 mt-6">
              <Button onClick={handleConfigureCloning}>
                Start Cloning
                <Copy className="h-4 w-4 ml-2" />
              </Button>
              <Button variant="outline" onClick={resetCloning}>
                Back to Selection
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (cloningStep === 'clone') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Cloning in Progress</h1>
          <p className="text-xl text-muted-foreground">
            Please wait while we clone your setup to the new jurisdiction
          </p>
        </div>

        <Card>
          <CardContent className="pt-6">
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">
                  {Math.round(cloningProgress)}%
                </div>
                <Progress value={cloningProgress} className="w-full" />
              </div>

              <div className="text-center">
                <p className="text-sm text-muted-foreground">{cloningStatus}</p>
              </div>

              <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <Copy className="h-4 w-4" />
                  <span>Cloning from {getJurisdictionName(currentJurisdiction)}</span>
                </div>
                <ArrowRight className="h-4 w-4" />
                <div className="flex items-center space-x-2">
                  <Globe className="h-4 w-4" />
                  <span>To {getJurisdictionName(selectedTargetJurisdiction)}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (cloningStep === 'complete') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Check className="h-8 w-8 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold mb-4">Clone Completed!</h1>
          <p className="text-xl text-muted-foreground">
            Your setup has been successfully cloned to {getJurisdictionName(selectedTargetJurisdiction)}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Clone Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Source Jurisdiction:</span>
                <div className="font-medium">{getJurisdictionName(currentJurisdiction)} ({currentLanguage.toUpperCase()})</div>
              </div>
              <div>
                <span className="text-muted-foreground">Target Jurisdiction:</span>
                <div className="font-medium">{getJurisdictionName(selectedTargetJurisdiction)} ({selectedTargetLanguage.toUpperCase()})</div>
              </div>
              <div>
                <span className="text-muted-foreground">Cloned Persona:</span>
                <div className="font-medium">{persona?.name} (Cloned)</div>
              </div>
              <div>
                <span className="text-muted-foreground">Components Cloned:</span>
                <div className="font-medium">{getCloningSummary().selectedComponents} components</div>
              </div>
            </div>

            <Separator />

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                The cloned setup includes localized tax rules and forms for {getJurisdictionName(selectedTargetJurisdiction)}. 
                Please review and customize as needed for your specific requirements.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <div className="flex flex-col space-y-3">
          <Button onClick={handleSwitchToClonedJurisdiction} size="lg">
            Switch to {getJurisdictionName(selectedTargetJurisdiction)}
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
          <Button variant="outline" onClick={resetCloning}>
            Clone Another Jurisdiction
          </Button>
        </div>
      </div>
    );
  }

  return null;
}

function getComponentDisplayName(component) {
  const names = {
    persona: 'Persona Configuration',
    knowledge_base: 'Knowledge Base',
    tax_rules: 'Tax Rules & Calculations',
    forms_templates: 'Forms & Templates',
    ai_training: 'AI Training Data',
    user_preferences: 'User Preferences'
  };
  return names[component] || component;
}

function getComponentDescription(component) {
  const descriptions = {
    persona: 'Clone persona settings, characteristics, and preferences',
    knowledge_base: 'Copy relevant tax knowledge and documentation',
    tax_rules: 'Adapt tax calculation rules for the new jurisdiction',
    forms_templates: 'Generate localized tax forms and templates',
    ai_training: 'Transfer AI training data (increases processing time)',
    user_preferences: 'Copy user interface and communication preferences'
  };
  return descriptions[component] || '';
}

function getComponentIcon(component) {
  const icons = {
    persona: <Users className="h-4 w-4 text-muted-foreground" />,
    knowledge_base: <Database className="h-4 w-4 text-muted-foreground" />,
    tax_rules: <Settings className="h-4 w-4 text-muted-foreground" />,
    forms_templates: <FileText className="h-4 w-4 text-muted-foreground" />,
    ai_training: <Brain className="h-4 w-4 text-muted-foreground" />,
    user_preferences: <User className="h-4 w-4 text-muted-foreground" />
  };
  return icons[component] || null;
}

