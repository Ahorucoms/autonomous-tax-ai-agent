import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Avatar, AvatarFallback } from './ui/avatar';
import { 
  User, 
  LogOut, 
  X,
  ChevronRight
} from 'lucide-react';

export function Sidebar({ 
  navigationItems, 
  currentView, 
  onViewChange, 
  user, 
  jurisdiction, 
  language, 
  selectedPersona,
  onSidebarClose 
}) {
  
  const handleNavigation = (viewId) => {
    onViewChange(viewId);
    if (onSidebarClose) {
      onSidebarClose();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('ai-tax-session');
    window.location.reload();
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">AI Tax Agent</h2>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onSidebarClose}
            className="lg:hidden"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        {/* User Info */}
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarFallback>
              <User className="h-5 w-5" />
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>

        {/* Context Info */}
        <div className="mt-3 space-y-2">
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-xs">
              {jurisdiction}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {language?.toUpperCase()}
            </Badge>
          </div>
          
          {selectedPersona && (
            <div className="flex items-center space-x-2">
              <Badge variant="default" className="text-xs">
                {selectedPersona.name}
              </Badge>
              <span className="text-xs text-muted-foreground">
                ({selectedPersona.type})
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto">
        <nav className="p-2">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const IconComponent = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full justify-start h-auto p-3 ${
                    isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => handleNavigation(item.id)}
                >
                  <div className="flex items-center space-x-3 w-full">
                    <IconComponent className="h-5 w-5 flex-shrink-0" />
                    <div className="flex-1 text-left">
                      <div className="font-medium text-sm">{item.label}</div>
                      <div className="text-xs opacity-70">{item.description}</div>
                    </div>
                    {isActive && (
                      <ChevronRight className="h-4 w-4 flex-shrink-0" />
                    )}
                  </div>
                </Button>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="space-y-2">
          <div className="text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Version:</span>
              <span>1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className="text-green-600">Online</span>
            </div>
          </div>
          
          <Separator />
          
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleLogout}
            className="w-full justify-start text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
}

