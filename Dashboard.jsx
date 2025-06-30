import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  CheckSquare, 
  FileText, 
  BookOpen, 
  Settings,
  Plus,
  TrendingUp,
  Calendar,
  AlertCircle,
  Clock,
  CheckCircle,
  User,
  Building,
  Calculator,
  Upload
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const Dashboard = ({ user, onNavigate, onTaskCreate }) => {
  const [activeTab, setActiveTab] = useState('overview')

  const stats = [
    {
      title: 'Active Tasks',
      value: '3',
      change: '+2 from last week',
      icon: CheckSquare,
      color: 'text-blue-600'
    },
    {
      title: 'Documents',
      value: '12',
      change: '+4 this month',
      icon: FileText,
      color: 'text-green-600'
    },
    {
      title: 'Tax Saved',
      value: '€2,340',
      change: 'This year',
      icon: TrendingUp,
      color: 'text-purple-600'
    },
    {
      title: 'Compliance',
      value: '98%',
      change: 'All deadlines met',
      icon: CheckCircle,
      color: 'text-emerald-600'
    }
  ]

  const recentTasks = [
    {
      id: 1,
      title: 'Income Tax Return 2024',
      status: 'in_progress',
      priority: 'high',
      dueDate: '2024-07-31',
      progress: 75,
      type: 'income_tax'
    },
    {
      id: 2,
      title: 'Q2 VAT Return',
      status: 'waiting_info',
      priority: 'medium',
      dueDate: '2024-07-15',
      progress: 40,
      type: 'vat'
    },
    {
      id: 3,
      title: 'Provisional Tax Payment',
      status: 'draft',
      priority: 'low',
      dueDate: '2024-08-31',
      progress: 10,
      type: 'provisional'
    }
  ]

  const upcomingDeadlines = [
    {
      title: 'VAT Return Q2',
      date: '2024-07-15',
      daysLeft: 5,
      type: 'vat'
    },
    {
      title: 'Income Tax Return',
      date: '2024-07-31',
      daysLeft: 21,
      type: 'income_tax'
    },
    {
      title: 'Provisional Tax',
      date: '2024-08-31',
      daysLeft: 52,
      type: 'provisional'
    }
  ]

  const quickActions = [
    {
      title: 'Calculate Income Tax',
      description: 'Quick tax calculation',
      icon: Calculator,
      action: 'calculate_income_tax',
      color: 'bg-blue-500'
    },
    {
      title: 'Upload Documents',
      description: 'Add tax documents',
      icon: Upload,
      action: 'upload_documents',
      color: 'bg-green-500'
    },
    {
      title: 'File VAT Return',
      description: 'Submit VAT filing',
      icon: FileText,
      action: 'file_vat',
      color: 'bg-purple-500'
    },
    {
      title: 'New Task',
      description: 'Create custom task',
      icon: Plus,
      action: 'new_task',
      color: 'bg-orange-500'
    }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'in_progress': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'waiting_info': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'draft': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-MT', {
      day: 'numeric',
      month: 'short'
    })
  }

  const handleQuickAction = (action) => {
    if (onTaskCreate) {
      onTaskCreate({
        type: 'create_task',
        template: action,
        title: quickActions.find(qa => qa.action === action)?.title
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <LayoutDashboard className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Welcome back, {user?.name || 'User'}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {user?.userType === 'individual' && <><User className="w-4 h-4 inline mr-1" />Individual Taxpayer</>}
                  {user?.userType === 'business' && <><Building className="w-4 h-4 inline mr-1" />Business Owner</>}
                  {user?.userType === 'advisor' && <><User className="w-4 h-4 inline mr-1" />Tax Advisor</>}
                  {user?.userType === 'vsp' && <><Building className="w-4 h-4 inline mr-1" />VSP</>}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-xs">
                🇲🇹 Malta
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigate('settings')}
                className="min-h-[44px]"
              >
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="calendar">Calendar</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat, index) => {
                const Icon = stat.icon
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                              {stat.title}
                            </p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                              {stat.value}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {stat.change}
                            </p>
                          </div>
                          <Icon className={`w-8 h-8 ${stat.color}`} />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )
              })}
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks to get you started quickly
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {quickActions.map((action, index) => {
                    const Icon = action.icon
                    return (
                      <motion.div
                        key={index}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Button
                          variant="outline"
                          className="h-auto p-4 flex flex-col items-center space-y-2 w-full min-h-[44px]"
                          onClick={() => handleQuickAction(action.action)}
                        >
                          <div className={`w-10 h-10 rounded-lg ${action.color} flex items-center justify-center`}>
                            <Icon className="w-5 h-5 text-white" />
                          </div>
                          <div className="text-center">
                            <p className="font-medium text-sm">{action.title}</p>
                            <p className="text-xs text-gray-500">{action.description}</p>
                          </div>
                        </Button>
                      </motion.div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Recent Tasks and Deadlines */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Tasks */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Tasks</CardTitle>
                  <CardDescription>
                    Your latest tax-related activities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recentTasks.map((task) => (
                    <div key={task.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm">{task.title}</h4>
                        <div className="flex items-center space-x-2">
                          <Badge className={getPriorityColor(task.priority)}>
                            {task.priority}
                          </Badge>
                          <Badge className={getStatusColor(task.status)}>
                            {task.status.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">Progress</span>
                          <span className="font-medium">{task.progress}%</span>
                        </div>
                        <Progress value={task.progress} className="h-2" />
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400 flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          Due {formatDate(task.dueDate)}
                        </span>
                        <Button variant="ghost" size="sm" className="h-8">
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Upcoming Deadlines */}
              <Card>
                <CardHeader>
                  <CardTitle>Upcoming Deadlines</CardTitle>
                  <CardDescription>
                    Important dates to keep in mind
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {upcomingDeadlines.map((deadline, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          deadline.daysLeft <= 7 ? 'bg-red-100 text-red-600' :
                          deadline.daysLeft <= 30 ? 'bg-yellow-100 text-yellow-600' :
                          'bg-green-100 text-green-600'
                        }`}>
                          {deadline.daysLeft <= 7 ? <AlertCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                        </div>
                        <div>
                          <p className="font-medium text-sm">{deadline.title}</p>
                          <p className="text-xs text-gray-500">{formatDate(deadline.date)}</p>
                        </div>
                      </div>
                      <Badge variant={deadline.daysLeft <= 7 ? 'destructive' : 'secondary'}>
                        {deadline.daysLeft} days
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="tasks">
            <Card>
              <CardHeader>
                <CardTitle>All Tasks</CardTitle>
                <CardDescription>
                  Manage your tax-related tasks and activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <CheckSquare className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Task Management</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Detailed task management interface coming soon
                  </p>
                  <Button onClick={() => handleQuickAction('new_task')}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create New Task
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <CardTitle>Document Vault</CardTitle>
                <CardDescription>
                  Your secure document storage and management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Document Management</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Upload, organize, and manage your tax documents
                  </p>
                  <Button onClick={() => handleQuickAction('upload_documents')}>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Documents
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="calendar">
            <Card>
              <CardHeader>
                <CardTitle>Tax Calendar</CardTitle>
                <CardDescription>
                  Important dates and deadlines for Malta tax compliance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Tax Calendar</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Interactive calendar with all Malta tax deadlines
                  </p>
                  <Button variant="outline">
                    View Full Calendar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default Dashboard

