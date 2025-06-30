import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  User, 
  Building2, 
  Users, 
  Briefcase, 
  Home, 
  Plus,
  Edit,
  Trash2,
  Star,
  Check
} from 'lucide-react';

export function PersonaSelector({ 
  jurisdiction, 
  language, 
  currentPersona, 
  onPersonaSelect, 
  showHeader = false 
}) {
  const [personas, setPersonas] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState(currentPersona);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingPersona, setEditingPersona] = useState(null);

  useEffect(() => {
    loadPersonas();
  }, [jurisdiction, language]);

  const loadPersonas = () => {
    // Load personas from localStorage or create defaults
    const savedPersonas = localStorage.getItem(`personas-${jurisdiction}-${language}`);
    
    if (savedPersonas) {
      setPersonas(JSON.parse(savedPersonas));
    } else {
      // Create default personas based on jurisdiction
      const defaultPersonas = getDefaultPersonas(jurisdiction, language);
      setPersonas(defaultPersonas);
      localStorage.setItem(`personas-${jurisdiction}-${language}`, JSON.stringify(defaultPersonas));
    }
  };

  const getDefaultPersonas = (jurisdiction, language) => {
    const basePersonas = [
      {
        id: 'individual-employee',
        name: language === 'fr' ? 'Employé Individuel' : 'Individual Employee',
        description: language === 'fr' 
          ? 'Employé salarié avec revenus principalement du travail'
          : 'Salaried employee with income primarily from employment',
        type: 'individual',
        icon: User,
        characteristics: {
          employment_status: 'employed',
          income_sources: ['salary'],
          tax_complexity: 'simple',
          filing_frequency: 'annual'
        },
        preferences: {
          communication_style: 'simple',
          detail_level: 'basic',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      },
      {
        id: 'self-employed',
        name: language === 'fr' ? 'Travailleur Indépendant' : 'Self-Employed Professional',
        description: language === 'fr'
          ? 'Professionnel indépendant avec revenus d\'activité'
          : 'Independent professional with business income',
        type: 'individual',
        icon: Briefcase,
        characteristics: {
          employment_status: 'self_employed',
          income_sources: ['business', 'professional_fees'],
          tax_complexity: 'moderate',
          filing_frequency: 'quarterly'
        },
        preferences: {
          communication_style: 'detailed',
          detail_level: 'intermediate',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      },
      {
        id: 'small-business',
        name: language === 'fr' ? 'Petite Entreprise' : 'Small Business Owner',
        description: language === 'fr'
          ? 'Propriétaire de petite entreprise avec employés'
          : 'Small business owner with employees',
        type: 'business',
        icon: Building2,
        characteristics: {
          business_type: 'small_business',
          employee_count: '1-10',
          revenue_range: 'under_500k',
          tax_complexity: 'complex'
        },
        preferences: {
          communication_style: 'professional',
          detail_level: 'advanced',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      },
      {
        id: 'family-household',
        name: language === 'fr' ? 'Foyer Familial' : 'Family Household',
        description: language === 'fr'
          ? 'Famille avec enfants et revenus multiples'
          : 'Family with children and multiple income sources',
        type: 'family',
        icon: Home,
        characteristics: {
          marital_status: 'married',
          dependents: 'yes',
          income_sources: ['salary', 'investment'],
          tax_complexity: 'moderate'
        },
        preferences: {
          communication_style: 'friendly',
          detail_level: 'intermediate',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      }
    ];

    // Add jurisdiction-specific personas
    if (jurisdiction === 'MT') {
      basePersonas.push({
        id: 'malta-resident',
        name: language === 'en' ? 'Malta Tax Resident' : 'Resident Fiscal Malta',
        description: language === 'en'
          ? 'Malta tax resident with local and foreign income'
          : 'Résident fiscal maltais avec revenus locaux et étrangers',
        type: 'individual',
        icon: Users,
        characteristics: {
          tax_residency: 'malta',
          income_sources: ['salary', 'foreign_income'],
          tax_complexity: 'moderate',
          special_considerations: ['foreign_tax_credits', 'malta_refund_system']
        },
        preferences: {
          communication_style: 'detailed',
          detail_level: 'intermediate',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      });
    }

    if (jurisdiction === 'FR') {
      basePersonas.push({
        id: 'french-resident',
        name: 'Résident Fiscal Français',
        description: 'Résident fiscal français avec revenus diversifiés',
        type: 'individual',
        icon: Users,
        characteristics: {
          tax_residency: 'france',
          income_sources: ['salary', 'investment', 'rental'],
          tax_complexity: 'complex',
          special_considerations: ['quotient_familial', 'niches_fiscales']
        },
        preferences: {
          communication_style: 'formal',
          detail_level: 'advanced',
          examples_preferred: true
        },
        jurisdiction,
        language,
        isDefault: true,
        created_at: new Date().toISOString()
      });
    }

    return basePersonas;
  };

  const handlePersonaSelect = (persona) => {
    setSelectedPersona(persona);
    if (onPersonaSelect) {
      onPersonaSelect(persona);
    }
  };

  const handleCreatePersona = (personaData) => {
    const newPersona = {
      id: `custom-${Date.now()}`,
      ...personaData,
      jurisdiction,
      language,
      isDefault: false,
      created_at: new Date().toISOString()
    };

    const updatedPersonas = [...personas, newPersona];
    setPersonas(updatedPersonas);
    localStorage.setItem(`personas-${jurisdiction}-${language}`, JSON.stringify(updatedPersonas));
    
    setShowCreateDialog(false);
    handlePersonaSelect(newPersona);
  };

  const handleEditPersona = (personaData) => {
    const updatedPersonas = personas.map(p => 
      p.id === editingPersona.id 
        ? { ...p, ...personaData, updated_at: new Date().toISOString() }
        : p
    );
    
    setPersonas(updatedPersonas);
    localStorage.setItem(`personas-${jurisdiction}-${language}`, JSON.stringify(updatedPersonas));
    
    setEditingPersona(null);
    
    // Update selected persona if it was edited
    if (selectedPersona?.id === editingPersona.id) {
      const updatedPersona = updatedPersonas.find(p => p.id === editingPersona.id);
      setSelectedPersona(updatedPersona);
      if (onPersonaSelect) {
        onPersonaSelect(updatedPersona);
      }
    }
  };

  const handleDeletePersona = (personaId) => {
    if (personas.find(p => p.id === personaId)?.isDefault) {
      return; // Can't delete default personas
    }

    const updatedPersonas = personas.filter(p => p.id !== personaId);
    setPersonas(updatedPersonas);
    localStorage.setItem(`personas-${jurisdiction}-${language}`, JSON.stringify(updatedPersonas));
    
    // If deleted persona was selected, clear selection
    if (selectedPersona?.id === personaId) {
      setSelectedPersona(null);
    }
  };

  const getPersonaIcon = (persona) => {
    const IconComponent = persona.icon || User;
    return <IconComponent className="h-8 w-8" />;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {showHeader && (
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            {language === 'fr' ? 'Gestion des Personas' : 'Persona Management'}
          </h1>
          <p className="text-muted-foreground">
            {language === 'fr' 
              ? 'Sélectionnez ou créez un persona pour personnaliser votre expérience fiscale'
              : 'Select or create a persona to customize your tax experience'
            }
          </p>
        </div>
      )}

      {!showHeader && (
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">
            {language === 'fr' ? 'Choisissez Votre Persona' : 'Choose Your Persona'}
          </h1>
          <p className="text-xl text-muted-foreground mb-2">
            {language === 'fr' 
              ? 'Sélectionnez le profil qui correspond le mieux à votre situation'
              : 'Select the profile that best matches your situation'
            }
          </p>
          <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
            <Badge variant="secondary">{jurisdiction}</Badge>
            <span>•</span>
            <Badge variant="outline">{language.toUpperCase()}</Badge>
          </div>
        </div>
      )}

      {/* Persona Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {personas.map((persona) => (
          <Card 
            key={persona.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedPersona?.id === persona.id 
                ? 'ring-2 ring-primary border-primary' 
                : 'hover:border-primary/50'
            }`}
            onClick={() => handlePersonaSelect(persona)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${
                    selectedPersona?.id === persona.id 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted'
                  }`}>
                    {getPersonaIcon(persona)}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{persona.name}</CardTitle>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {persona.type}
                      </Badge>
                      {persona.isDefault && (
                        <Badge variant="secondary" className="text-xs">
                          <Star className="h-3 w-3 mr-1" />
                          {language === 'fr' ? 'Défaut' : 'Default'}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                
                {selectedPersona?.id === persona.id && (
                  <div className="bg-primary text-primary-foreground rounded-full p-1">
                    <Check className="h-4 w-4" />
                  </div>
                )}
              </div>
            </CardHeader>
            
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                {persona.description}
              </p>
              
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1">
                  {Object.entries(persona.characteristics).slice(0, 3).map(([key, value]) => (
                    <Badge key={key} variant="secondary" className="text-xs">
                      {String(value).replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
                
                {!persona.isDefault && (
                  <div className="flex items-center justify-end space-x-2 pt-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingPersona(persona);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeletePersona(persona.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Create New Persona Card */}
        <Card 
          className="cursor-pointer border-dashed border-2 hover:border-primary/50 transition-colors"
          onClick={() => setShowCreateDialog(true)}
        >
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[200px] text-center">
            <div className="bg-muted p-4 rounded-lg mb-4">
              <Plus className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold mb-2">
              {language === 'fr' ? 'Créer un Nouveau Persona' : 'Create New Persona'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {language === 'fr' 
                ? 'Personnalisez votre profil fiscal'
                : 'Customize your tax profile'
              }
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      {!showHeader && selectedPersona && (
        <div className="text-center">
          <Button 
            size="lg" 
            onClick={() => onPersonaSelect(selectedPersona)}
            className="px-8"
          >
            {language === 'fr' ? 'Continuer avec ce Persona' : 'Continue with this Persona'}
          </Button>
        </div>
      )}

      {/* Create/Edit Persona Dialog */}
      <PersonaDialog
        open={showCreateDialog || !!editingPersona}
        onOpenChange={(open) => {
          if (!open) {
            setShowCreateDialog(false);
            setEditingPersona(null);
          }
        }}
        persona={editingPersona}
        jurisdiction={jurisdiction}
        language={language}
        onSave={editingPersona ? handleEditPersona : handleCreatePersona}
      />
    </div>
  );
}

function PersonaDialog({ open, onOpenChange, persona, jurisdiction, language, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'individual',
    characteristics: {},
    preferences: {}
  });

  useEffect(() => {
    if (persona) {
      setFormData({
        name: persona.name,
        description: persona.description,
        type: persona.type,
        characteristics: persona.characteristics || {},
        preferences: persona.preferences || {}
      });
    } else {
      setFormData({
        name: '',
        description: '',
        type: 'individual',
        characteristics: {},
        preferences: {}
      });
    }
  }, [persona]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const updateCharacteristic = (key, value) => {
    setFormData(prev => ({
      ...prev,
      characteristics: {
        ...prev.characteristics,
        [key]: value
      }
    }));
  };

  const updatePreference = (key, value) => {
    setFormData(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {persona 
              ? (language === 'fr' ? 'Modifier le Persona' : 'Edit Persona')
              : (language === 'fr' ? 'Créer un Nouveau Persona' : 'Create New Persona')
            }
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">
                {language === 'fr' ? 'Nom du Persona' : 'Persona Name'}
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder={language === 'fr' ? 'Ex: Entrepreneur Tech' : 'e.g., Tech Entrepreneur'}
                required
              />
            </div>

            <div>
              <Label htmlFor="description">
                {language === 'fr' ? 'Description' : 'Description'}
              </Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder={language === 'fr' 
                  ? 'Décrivez ce persona et sa situation fiscale'
                  : 'Describe this persona and their tax situation'
                }
                required
              />
            </div>

            <div>
              <Label htmlFor="type">
                {language === 'fr' ? 'Type de Persona' : 'Persona Type'}
              </Label>
              <Select 
                value={formData.type} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="individual">
                    {language === 'fr' ? 'Individuel' : 'Individual'}
                  </SelectItem>
                  <SelectItem value="business">
                    {language === 'fr' ? 'Entreprise' : 'Business'}
                  </SelectItem>
                  <SelectItem value="family">
                    {language === 'fr' ? 'Famille' : 'Family'}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          {/* Characteristics */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">
              {language === 'fr' ? 'Caractéristiques' : 'Characteristics'}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>
                  {language === 'fr' ? 'Statut d\'emploi' : 'Employment Status'}
                </Label>
                <Select 
                  value={formData.characteristics.employment_status || ''} 
                  onValueChange={(value) => updateCharacteristic('employment_status', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={language === 'fr' ? 'Sélectionner' : 'Select'} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="employed">
                      {language === 'fr' ? 'Employé' : 'Employed'}
                    </SelectItem>
                    <SelectItem value="self_employed">
                      {language === 'fr' ? 'Indépendant' : 'Self-employed'}
                    </SelectItem>
                    <SelectItem value="business_owner">
                      {language === 'fr' ? 'Chef d\'entreprise' : 'Business Owner'}
                    </SelectItem>
                    <SelectItem value="retired">
                      {language === 'fr' ? 'Retraité' : 'Retired'}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>
                  {language === 'fr' ? 'Complexité fiscale' : 'Tax Complexity'}
                </Label>
                <Select 
                  value={formData.characteristics.tax_complexity || ''} 
                  onValueChange={(value) => updateCharacteristic('tax_complexity', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={language === 'fr' ? 'Sélectionner' : 'Select'} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="simple">
                      {language === 'fr' ? 'Simple' : 'Simple'}
                    </SelectItem>
                    <SelectItem value="moderate">
                      {language === 'fr' ? 'Modérée' : 'Moderate'}
                    </SelectItem>
                    <SelectItem value="complex">
                      {language === 'fr' ? 'Complexe' : 'Complex'}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Separator />

          {/* Preferences */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">
              {language === 'fr' ? 'Préférences' : 'Preferences'}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>
                  {language === 'fr' ? 'Style de communication' : 'Communication Style'}
                </Label>
                <Select 
                  value={formData.preferences.communication_style || ''} 
                  onValueChange={(value) => updatePreference('communication_style', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={language === 'fr' ? 'Sélectionner' : 'Select'} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="simple">
                      {language === 'fr' ? 'Simple' : 'Simple'}
                    </SelectItem>
                    <SelectItem value="detailed">
                      {language === 'fr' ? 'Détaillé' : 'Detailed'}
                    </SelectItem>
                    <SelectItem value="professional">
                      {language === 'fr' ? 'Professionnel' : 'Professional'}
                    </SelectItem>
                    <SelectItem value="friendly">
                      {language === 'fr' ? 'Amical' : 'Friendly'}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>
                  {language === 'fr' ? 'Niveau de détail' : 'Detail Level'}
                </Label>
                <Select 
                  value={formData.preferences.detail_level || ''} 
                  onValueChange={(value) => updatePreference('detail_level', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={language === 'fr' ? 'Sélectionner' : 'Select'} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic">
                      {language === 'fr' ? 'Basique' : 'Basic'}
                    </SelectItem>
                    <SelectItem value="intermediate">
                      {language === 'fr' ? 'Intermédiaire' : 'Intermediate'}
                    </SelectItem>
                    <SelectItem value="advanced">
                      {language === 'fr' ? 'Avancé' : 'Advanced'}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </Button>
            <Button type="submit">
              {persona 
                ? (language === 'fr' ? 'Mettre à jour' : 'Update')
                : (language === 'fr' ? 'Créer' : 'Create')
              }
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

