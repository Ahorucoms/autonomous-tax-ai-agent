"""
Reporting and Analytics Service for Malta Tax AI Agent
Comprehensive reporting capabilities for tax analytics and business intelligence
"""

import os
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
import uuid
from enum import Enum
import calendar

class ReportType(Enum):
    FILING_SUMMARY = "filing_summary"
    REVENUE_ANALYSIS = "revenue_analysis"
    COMPLIANCE_REPORT = "compliance_report"
    USER_ACTIVITY = "user_activity"
    PERFORMANCE_METRICS = "performance_metrics"
    TAX_BREAKDOWN = "tax_breakdown"
    AUDIT_REPORT = "audit_report"
    CUSTOM_REPORT = "custom_report"

class ReportFormat(Enum):
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"

class ReportingService:
    """Reporting and analytics service for Malta Tax AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Storage for reports and analytics data
        self.reports = {}
        self.scheduled_reports = {}
        self.analytics_data = {}
        
        # Initialize sample data for reporting
        self._initialize_sample_data()
        
        # Report templates
        self.report_templates = {}
        self._initialize_report_templates()
    
    def _initialize_sample_data(self):
        """Initialize sample analytics data for reporting"""
        # Generate sample filing data for the last 12 months
        self.analytics_data = {
            'filings': self._generate_filing_data(),
            'revenue': self._generate_revenue_data(),
            'users': self._generate_user_data(),
            'compliance': self._generate_compliance_data(),
            'performance': self._generate_performance_data(),
            'tax_breakdown': self._generate_tax_breakdown_data()
        }
    
    def _generate_filing_data(self) -> List[Dict[str, Any]]:
        """Generate sample filing data"""
        filing_data = []
        base_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(12):  # 12 months of data
            month_date = base_date + timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            # Generate filing statistics for each month
            month_data = {
                'month': month_name,
                'month_date': month_date.isoformat(),
                'total_filings': 120 + (i * 15) + (i % 3 * 20),
                'income_tax_individual': 45 + (i * 5),
                'income_tax_corporate': 12 + (i * 2),
                'vat_returns': 35 + (i * 3),
                'social_security_class1': 20 + (i * 2),
                'social_security_class2': 8 + i,
                'successful_filings': 115 + (i * 14),
                'failed_filings': 5 + i,
                'pending_filings': 3 + (i % 2),
                'processing_time_avg': 2.5 + (i * 0.1),
                'user_satisfaction': 4.2 + (i * 0.05)
            }
            filing_data.append(month_data)
        
        return filing_data
    
    def _generate_revenue_data(self) -> List[Dict[str, Any]]:
        """Generate sample revenue data"""
        revenue_data = []
        base_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(12):  # 12 months of data
            month_date = base_date + timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            # Generate revenue statistics for each month
            base_revenue = 250000 + (i * 25000)
            month_data = {
                'month': month_name,
                'month_date': month_date.isoformat(),
                'total_revenue': base_revenue + (i % 4 * 15000),
                'income_tax_revenue': base_revenue * 0.6,
                'vat_revenue': base_revenue * 0.25,
                'social_security_revenue': base_revenue * 0.12,
                'other_revenue': base_revenue * 0.03,
                'processing_fees': 5000 + (i * 500),
                'penalty_revenue': 2000 + (i * 200),
                'refunds_issued': 15000 + (i * 1500),
                'outstanding_payments': 8000 + (i * 800),
                'collection_rate': 94.5 + (i * 0.2)
            }
            revenue_data.append(month_data)
        
        return revenue_data
    
    def _generate_user_data(self) -> List[Dict[str, Any]]:
        """Generate sample user activity data"""
        user_data = []
        base_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(12):  # 12 months of data
            month_date = base_date + timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            # Generate user activity statistics for each month
            month_data = {
                'month': month_name,
                'month_date': month_date.isoformat(),
                'new_registrations': 25 + (i * 3) + (i % 3 * 5),
                'active_users': 150 + (i * 12),
                'total_users': 500 + (i * 25),
                'user_sessions': 1200 + (i * 100),
                'avg_session_duration': 15.5 + (i * 0.5),
                'bounce_rate': 25.0 - (i * 0.3),
                'feature_usage': {
                    'tax_calculator': 85 + i,
                    'document_upload': 65 + (i * 2),
                    'filing_submission': 45 + (i * 3),
                    'payment_processing': 40 + (i * 2),
                    'compliance_check': 30 + i
                },
                'user_satisfaction_score': 4.1 + (i * 0.05),
                'support_tickets': 15 - i if i < 10 else 5
            }
            user_data.append(month_data)
        
        return user_data
    
    def _generate_compliance_data(self) -> List[Dict[str, Any]]:
        """Generate sample compliance data"""
        compliance_data = []
        base_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(12):  # 12 months of data
            month_date = base_date + timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            # Generate compliance statistics for each month
            month_data = {
                'month': month_name,
                'month_date': month_date.isoformat(),
                'compliance_score': 92.5 + (i * 0.5),
                'on_time_filings': 95.2 + (i * 0.3),
                'late_filings': 4.8 - (i * 0.3),
                'compliance_violations': 8 - i if i < 6 else 2,
                'penalty_assessments': 12 - i if i < 8 else 4,
                'audit_requests': 3 + (i % 3),
                'regulatory_updates': 2 + (i % 2),
                'deadline_adherence': 96.8 + (i * 0.2),
                'documentation_completeness': 94.5 + (i * 0.4),
                'risk_score': 15.0 - (i * 0.5) if i < 10 else 10.0
            }
            compliance_data.append(month_data)
        
        return compliance_data
    
    def _generate_performance_data(self) -> List[Dict[str, Any]]:
        """Generate sample performance data"""
        performance_data = []
        base_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(12):  # 12 months of data
            month_date = base_date + timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            # Generate performance statistics for each month
            month_data = {
                'month': month_name,
                'month_date': month_date.isoformat(),
                'avg_response_time': 1.2 - (i * 0.05) if i < 10 else 0.7,
                'system_uptime': 99.5 + (i * 0.03),
                'api_success_rate': 98.5 + (i * 0.1),
                'error_rate': 1.5 - (i * 0.1) if i < 10 else 0.5,
                'throughput_requests_per_second': 150 + (i * 10),
                'database_performance': 95.0 + (i * 0.3),
                'storage_usage_gb': 500 + (i * 50),
                'bandwidth_usage_gb': 1000 + (i * 100),
                'cpu_utilization': 65.0 - (i * 1.0) if i < 20 else 45.0,
                'memory_utilization': 70.0 - (i * 0.8) if i < 25 else 50.0,
                'concurrent_users': 50 + (i * 5)
            }
            performance_data.append(month_data)
        
        return performance_data
    
    def _generate_tax_breakdown_data(self) -> Dict[str, Any]:
        """Generate sample tax breakdown data"""
        return {
            'by_tax_type': {
                'income_tax_individual': {
                    'total_amount': 2500000.00,
                    'percentage': 45.5,
                    'filings_count': 1250,
                    'avg_amount': 2000.00
                },
                'income_tax_corporate': {
                    'total_amount': 1800000.00,
                    'percentage': 32.7,
                    'filings_count': 180,
                    'avg_amount': 10000.00
                },
                'vat': {
                    'total_amount': 900000.00,
                    'percentage': 16.4,
                    'filings_count': 450,
                    'avg_amount': 2000.00
                },
                'social_security': {
                    'total_amount': 300000.00,
                    'percentage': 5.4,
                    'filings_count': 600,
                    'avg_amount': 500.00
                }
            },
            'by_user_type': {
                'individual': {
                    'total_amount': 2200000.00,
                    'percentage': 40.0,
                    'users_count': 1500
                },
                'business': {
                    'total_amount': 2800000.00,
                    'percentage': 50.9,
                    'users_count': 300
                },
                'tax_professional': {
                    'total_amount': 500000.00,
                    'percentage': 9.1,
                    'users_count': 50
                }
            },
            'by_region': {
                'valletta': {'amount': 1650000.00, 'percentage': 30.0},
                'sliema': {'amount': 1100000.00, 'percentage': 20.0},
                'birkirkara': {'amount': 825000.00, 'percentage': 15.0},
                'qormi': {'amount': 550000.00, 'percentage': 10.0},
                'mosta': {'amount': 550000.00, 'percentage': 10.0},
                'other': {'amount': 825000.00, 'percentage': 15.0}
            }
        }
    
    def _initialize_report_templates(self):
        """Initialize report templates"""
        self.report_templates = {
            'filing_summary': {
                'name': 'Filing Summary Report',
                'description': 'Comprehensive overview of filing activities and statistics',
                'sections': [
                    'executive_summary',
                    'filing_statistics',
                    'processing_metrics',
                    'user_activity',
                    'trends_analysis'
                ],
                'default_period': 'monthly',
                'charts': ['filing_trends', 'success_rates', 'processing_times']
            },
            'revenue_analysis': {
                'name': 'Revenue Analysis Report',
                'description': 'Detailed analysis of tax revenue and financial metrics',
                'sections': [
                    'revenue_overview',
                    'tax_type_breakdown',
                    'collection_efficiency',
                    'forecasting',
                    'recommendations'
                ],
                'default_period': 'quarterly',
                'charts': ['revenue_trends', 'tax_breakdown', 'collection_rates']
            },
            'compliance_report': {
                'name': 'Compliance Report',
                'description': 'Compliance status and regulatory adherence analysis',
                'sections': [
                    'compliance_overview',
                    'deadline_adherence',
                    'violation_analysis',
                    'risk_assessment',
                    'improvement_plan'
                ],
                'default_period': 'monthly',
                'charts': ['compliance_trends', 'violation_types', 'risk_scores']
            },
            'user_activity': {
                'name': 'User Activity Report',
                'description': 'User engagement and system usage analysis',
                'sections': [
                    'user_overview',
                    'activity_metrics',
                    'feature_usage',
                    'satisfaction_analysis',
                    'growth_trends'
                ],
                'default_period': 'monthly',
                'charts': ['user_growth', 'activity_trends', 'feature_usage']
            }
        }
    
    def generate_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report based on configuration"""
        try:
            # Validate report configuration
            required_fields = ['report_type', 'period_start', 'period_end']
            for field in required_fields:
                if field not in report_config:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Validate report type
            try:
                ReportType(report_config['report_type'])
            except ValueError:
                return {
                    'success': False,
                    'error': 'Invalid report type'
                }
            
            # Generate report ID
            report_id = str(uuid.uuid4())
            
            # Create report based on type
            report_type = report_config['report_type']
            
            if report_type == ReportType.FILING_SUMMARY.value:
                report_data = self._generate_filing_summary_report(report_config)
            elif report_type == ReportType.REVENUE_ANALYSIS.value:
                report_data = self._generate_revenue_analysis_report(report_config)
            elif report_type == ReportType.COMPLIANCE_REPORT.value:
                report_data = self._generate_compliance_report(report_config)
            elif report_type == ReportType.USER_ACTIVITY.value:
                report_data = self._generate_user_activity_report(report_config)
            elif report_type == ReportType.PERFORMANCE_METRICS.value:
                report_data = self._generate_performance_metrics_report(report_config)
            elif report_type == ReportType.TAX_BREAKDOWN.value:
                report_data = self._generate_tax_breakdown_report(report_config)
            elif report_type == ReportType.CUSTOM_REPORT.value:
                report_data = self._generate_custom_report(report_config)
            else:
                return {
                    'success': False,
                    'error': 'Report type not implemented'
                }
            
            # Create report record
            report = {
                'report_id': report_id,
                'report_type': report_type,
                'title': report_data['title'],
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': report_config.get('user_id', 'system'),
                'period_start': report_config['period_start'],
                'period_end': report_config['period_end'],
                'format': report_config.get('format', ReportFormat.JSON.value),
                'status': 'completed',
                'data': report_data,
                'file_path': None,
                'download_url': None
            }
            
            # Store report
            self.reports[report_id] = report
            
            return {
                'success': True,
                'report_id': report_id,
                'report': report
            }
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise ValueError(f"Report generation failed: {str(e)}")
    
    def _generate_filing_summary_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate filing summary report"""
        filing_data = self.analytics_data['filings']
        
        # Filter data by period
        period_data = self._filter_data_by_period(filing_data, config['period_start'], config['period_end'])
        
        # Calculate summary statistics
        total_filings = sum(item['total_filings'] for item in period_data)
        successful_filings = sum(item['successful_filings'] for item in period_data)
        failed_filings = sum(item['failed_filings'] for item in period_data)
        avg_processing_time = sum(item['processing_time_avg'] for item in period_data) / len(period_data) if period_data else 0
        
        success_rate = (successful_filings / total_filings * 100) if total_filings > 0 else 0
        
        return {
            'title': 'Filing Summary Report',
            'period': f"{config['period_start']} to {config['period_end']}",
            'executive_summary': {
                'total_filings': total_filings,
                'successful_filings': successful_filings,
                'failed_filings': failed_filings,
                'success_rate': round(success_rate, 2),
                'avg_processing_time': round(avg_processing_time, 2)
            },
            'filing_breakdown': {
                'income_tax_individual': sum(item['income_tax_individual'] for item in period_data),
                'income_tax_corporate': sum(item['income_tax_corporate'] for item in period_data),
                'vat_returns': sum(item['vat_returns'] for item in period_data),
                'social_security_class1': sum(item['social_security_class1'] for item in period_data),
                'social_security_class2': sum(item['social_security_class2'] for item in period_data)
            },
            'monthly_trends': period_data,
            'key_insights': [
                f"Total of {total_filings} filings processed during the period",
                f"Success rate of {success_rate:.1f}% achieved",
                f"Average processing time of {avg_processing_time:.1f} minutes",
                "Income tax individual filings represent the largest category"
            ],
            'recommendations': [
                "Continue monitoring processing times for optimization opportunities",
                "Implement automated error detection to reduce failed filings",
                "Consider batch processing for high-volume periods"
            ]
        }
    
    def _generate_revenue_analysis_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate revenue analysis report"""
        revenue_data = self.analytics_data['revenue']
        tax_breakdown = self.analytics_data['tax_breakdown']
        
        # Filter data by period
        period_data = self._filter_data_by_period(revenue_data, config['period_start'], config['period_end'])
        
        # Calculate revenue statistics
        total_revenue = sum(item['total_revenue'] for item in period_data)
        total_fees = sum(item['processing_fees'] for item in period_data)
        total_penalties = sum(item['penalty_revenue'] for item in period_data)
        total_refunds = sum(item['refunds_issued'] for item in period_data)
        
        avg_collection_rate = sum(item['collection_rate'] for item in period_data) / len(period_data) if period_data else 0
        
        return {
            'title': 'Revenue Analysis Report',
            'period': f"{config['period_start']} to {config['period_end']}",
            'revenue_overview': {
                'total_revenue': total_revenue,
                'processing_fees': total_fees,
                'penalty_revenue': total_penalties,
                'refunds_issued': total_refunds,
                'net_revenue': total_revenue + total_fees + total_penalties - total_refunds,
                'collection_rate': round(avg_collection_rate, 2)
            },
            'tax_type_breakdown': tax_breakdown['by_tax_type'],
            'user_type_breakdown': tax_breakdown['by_user_type'],
            'regional_breakdown': tax_breakdown['by_region'],
            'monthly_trends': period_data,
            'growth_analysis': {
                'revenue_growth': self._calculate_growth_rate(period_data, 'total_revenue'),
                'collection_improvement': self._calculate_growth_rate(period_data, 'collection_rate'),
                'fee_growth': self._calculate_growth_rate(period_data, 'processing_fees')
            },
            'key_insights': [
                f"Total revenue of €{total_revenue:,.2f} generated during the period",
                f"Average collection rate of {avg_collection_rate:.1f}%",
                f"Processing fees contributed €{total_fees:,.2f}",
                "Income tax represents the largest revenue source"
            ],
            'recommendations': [
                "Focus on improving collection rates for outstanding payments",
                "Consider fee optimization for competitive positioning",
                "Implement automated penalty calculations for efficiency"
            ]
        }
    
    def _generate_compliance_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report"""
        compliance_data = self.analytics_data['compliance']
        
        # Filter data by period
        period_data = self._filter_data_by_period(compliance_data, config['period_start'], config['period_end'])
        
        # Calculate compliance statistics
        avg_compliance_score = sum(item['compliance_score'] for item in period_data) / len(period_data) if period_data else 0
        avg_on_time_rate = sum(item['on_time_filings'] for item in period_data) / len(period_data) if period_data else 0
        total_violations = sum(item['compliance_violations'] for item in period_data)
        total_penalties = sum(item['penalty_assessments'] for item in period_data)
        
        return {
            'title': 'Compliance Report',
            'period': f"{config['period_start']} to {config['period_end']}",
            'compliance_overview': {
                'overall_compliance_score': round(avg_compliance_score, 2),
                'on_time_filing_rate': round(avg_on_time_rate, 2),
                'total_violations': total_violations,
                'penalty_assessments': total_penalties,
                'audit_requests': sum(item['audit_requests'] for item in period_data)
            },
            'compliance_trends': period_data,
            'risk_assessment': {
                'high_risk_areas': ['Late filing penalties', 'Documentation completeness'],
                'improvement_areas': ['Deadline adherence', 'Regulatory updates'],
                'compliance_score_trend': 'Improving' if len(period_data) > 1 and period_data[-1]['compliance_score'] > period_data[0]['compliance_score'] else 'Stable'
            },
            'regulatory_updates': [
                'Updated VAT rates effective January 2025',
                'New social security contribution thresholds',
                'Enhanced documentation requirements for corporate filings'
            ],
            'key_insights': [
                f"Overall compliance score of {avg_compliance_score:.1f}%",
                f"On-time filing rate of {avg_on_time_rate:.1f}%",
                f"{total_violations} compliance violations identified",
                "Continuous improvement in compliance metrics observed"
            ],
            'recommendations': [
                "Implement automated deadline reminders",
                "Enhance documentation validation processes",
                "Provide compliance training for users",
                "Regular monitoring of regulatory changes"
            ]
        }
    
    def _generate_user_activity_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user activity report"""
        user_data = self.analytics_data['users']
        
        # Filter data by period
        period_data = self._filter_data_by_period(user_data, config['period_start'], config['period_end'])
        
        # Calculate user statistics
        total_registrations = sum(item['new_registrations'] for item in period_data)
        avg_active_users = sum(item['active_users'] for item in period_data) / len(period_data) if period_data else 0
        total_sessions = sum(item['user_sessions'] for item in period_data)
        avg_session_duration = sum(item['avg_session_duration'] for item in period_data) / len(period_data) if period_data else 0
        
        return {
            'title': 'User Activity Report',
            'period': f"{config['period_start']} to {config['period_end']}",
            'user_overview': {
                'new_registrations': total_registrations,
                'avg_active_users': round(avg_active_users, 0),
                'total_sessions': total_sessions,
                'avg_session_duration': round(avg_session_duration, 1),
                'user_satisfaction': round(sum(item['user_satisfaction_score'] for item in period_data) / len(period_data), 2) if period_data else 0
            },
            'activity_trends': period_data,
            'feature_usage_analysis': self._analyze_feature_usage(period_data),
            'user_engagement': {
                'high_engagement_features': ['Tax Calculator', 'Filing Submission'],
                'growth_opportunities': ['Document Upload', 'Compliance Check'],
                'user_retention_rate': 85.5,
                'churn_rate': 14.5
            },
            'key_insights': [
                f"{total_registrations} new users registered during the period",
                f"Average of {avg_active_users:.0f} active users per month",
                f"Total of {total_sessions} user sessions recorded",
                "Tax calculator is the most popular feature"
            ],
            'recommendations': [
                "Enhance onboarding process for new users",
                "Promote underutilized features through tutorials",
                "Implement user feedback collection system",
                "Optimize user interface based on usage patterns"
            ]
        }
    
    def _generate_performance_metrics_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance metrics report"""
        performance_data = self.analytics_data['performance']
        
        # Filter data by period
        period_data = self._filter_data_by_period(performance_data, config['period_start'], config['period_end'])
        
        # Calculate performance statistics
        avg_response_time = sum(item['avg_response_time'] for item in period_data) / len(period_data) if period_data else 0
        avg_uptime = sum(item['system_uptime'] for item in period_data) / len(period_data) if period_data else 0
        avg_success_rate = sum(item['api_success_rate'] for item in period_data) / len(period_data) if period_data else 0
        
        return {
            'title': 'Performance Metrics Report',
            'period': f"{config['period_start']} to {config['period_end']}",
            'performance_overview': {
                'avg_response_time': round(avg_response_time, 3),
                'system_uptime': round(avg_uptime, 2),
                'api_success_rate': round(avg_success_rate, 2),
                'avg_throughput': round(sum(item['throughput_requests_per_second'] for item in period_data) / len(period_data), 1) if period_data else 0,
                'avg_concurrent_users': round(sum(item['concurrent_users'] for item in period_data) / len(period_data), 0) if period_data else 0
            },
            'performance_trends': period_data,
            'system_health': {
                'cpu_utilization': 'Optimal',
                'memory_utilization': 'Good',
                'storage_usage': 'Moderate',
                'network_performance': 'Excellent'
            },
            'key_insights': [
                f"Average response time of {avg_response_time:.2f} seconds",
                f"System uptime of {avg_uptime:.1f}%",
                f"API success rate of {avg_success_rate:.1f}%",
                "Performance metrics within acceptable ranges"
            ],
            'recommendations': [
                "Continue monitoring response times",
                "Implement caching for frequently accessed data",
                "Consider load balancing for peak periods",
                "Regular performance optimization reviews"
            ]
        }
    
    def _generate_tax_breakdown_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tax breakdown report"""
        tax_breakdown = self.analytics_data['tax_breakdown']
        
        return {
            'title': 'Tax Breakdown Analysis',
            'period': f"{config['period_start']} to {config['period_end']}",
            'tax_type_analysis': tax_breakdown['by_tax_type'],
            'user_type_analysis': tax_breakdown['by_user_type'],
            'regional_analysis': tax_breakdown['by_region'],
            'key_insights': [
                "Income tax individual represents the largest tax category",
                "Business users contribute the highest revenue per user",
                "Valletta region shows highest tax collection",
                "VAT collections show steady growth"
            ],
            'recommendations': [
                "Focus on business user acquisition",
                "Expand services in high-revenue regions",
                "Optimize VAT processing workflows",
                "Implement targeted marketing by tax type"
            ]
        }
    
    def _generate_custom_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom report based on user specifications"""
        custom_config = config.get('custom_config', {})
        
        return {
            'title': custom_config.get('title', 'Custom Report'),
            'period': f"{config['period_start']} to {config['period_end']}",
            'custom_data': custom_config.get('data_sources', []),
            'custom_metrics': custom_config.get('metrics', []),
            'custom_charts': custom_config.get('charts', []),
            'key_insights': custom_config.get('insights', []),
            'recommendations': custom_config.get('recommendations', [])
        }
    
    def _filter_data_by_period(self, data: List[Dict[str, Any]], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Filter data by date period"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            filtered_data = []
            for item in data:
                item_date = datetime.fromisoformat(item['month_date'].replace('Z', '+00:00'))
                if start <= item_date <= end:
                    filtered_data.append(item)
            
            return filtered_data
        except Exception:
            # Return all data if date filtering fails
            return data
    
    def _calculate_growth_rate(self, data: List[Dict[str, Any]], field: str) -> float:
        """Calculate growth rate for a specific field"""
        if len(data) < 2:
            return 0.0
        
        try:
            first_value = data[0][field]
            last_value = data[-1][field]
            
            if first_value == 0:
                return 0.0
            
            growth_rate = ((last_value - first_value) / first_value) * 100
            return round(growth_rate, 2)
        except Exception:
            return 0.0
    
    def _analyze_feature_usage(self, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze feature usage patterns"""
        if not user_data:
            return {}
        
        # Aggregate feature usage across all periods
        total_usage = {}
        for period in user_data:
            feature_usage = period.get('feature_usage', {})
            for feature, usage in feature_usage.items():
                total_usage[feature] = total_usage.get(feature, 0) + usage
        
        # Calculate percentages
        total_all_features = sum(total_usage.values())
        feature_percentages = {}
        for feature, usage in total_usage.items():
            percentage = (usage / total_all_features * 100) if total_all_features > 0 else 0
            feature_percentages[feature] = round(percentage, 1)
        
        return {
            'total_usage': total_usage,
            'usage_percentages': feature_percentages,
            'most_popular': max(total_usage.items(), key=lambda x: x[1])[0] if total_usage else None,
            'least_popular': min(total_usage.items(), key=lambda x: x[1])[0] if total_usage else None
        }
    
    def get_report(self, report_id: str) -> Dict[str, Any]:
        """Get generated report by ID"""
        try:
            if report_id not in self.reports:
                return {
                    'success': False,
                    'error': 'Report not found'
                }
            
            return {
                'success': True,
                'report': self.reports[report_id]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting report: {str(e)}")
            raise ValueError(f"Report retrieval failed: {str(e)}")
    
    def get_reports(self, user_id: str = None, report_type: str = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated list of reports"""
        try:
            reports = list(self.reports.values())
            
            # Apply filters
            if user_id:
                reports = [r for r in reports if r['generated_by'] == user_id]
            if report_type:
                reports = [r for r in reports if r['report_type'] == report_type]
            
            # Sort by generation date (newest first)
            reports = sorted(reports, key=lambda r: r['generated_at'], reverse=True)
            
            # Pagination
            total_reports = len(reports)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_reports = reports[start_idx:end_idx]
            
            # Remove large data fields for list view
            summary_reports = []
            for report in paginated_reports:
                summary_report = report.copy()
                summary_report.pop('data', None)  # Remove large data field
                summary_reports.append(summary_report)
            
            return {
                'success': True,
                'reports': summary_reports,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_reports,
                    'pages': (total_reports + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting reports: {str(e)}")
            raise ValueError(f"Reports retrieval failed: {str(e)}")
    
    def get_report_templates(self) -> Dict[str, Any]:
        """Get available report templates"""
        return {
            'success': True,
            'templates': self.report_templates
        }
    
    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        try:
            # Get latest data from each category
            latest_filing = self.analytics_data['filings'][-1] if self.analytics_data['filings'] else {}
            latest_revenue = self.analytics_data['revenue'][-1] if self.analytics_data['revenue'] else {}
            latest_users = self.analytics_data['users'][-1] if self.analytics_data['users'] else {}
            latest_compliance = self.analytics_data['compliance'][-1] if self.analytics_data['compliance'] else {}
            latest_performance = self.analytics_data['performance'][-1] if self.analytics_data['performance'] else {}
            
            dashboard_data = {
                'overview_metrics': {
                    'total_filings_this_month': latest_filing.get('total_filings', 0),
                    'revenue_this_month': latest_revenue.get('total_revenue', 0),
                    'active_users': latest_users.get('active_users', 0),
                    'compliance_score': latest_compliance.get('compliance_score', 0),
                    'system_uptime': latest_performance.get('system_uptime', 0)
                },
                'filing_trends': self.analytics_data['filings'][-6:],  # Last 6 months
                'revenue_trends': self.analytics_data['revenue'][-6:],  # Last 6 months
                'user_growth': self.analytics_data['users'][-6:],  # Last 6 months
                'tax_breakdown': self.analytics_data['tax_breakdown'],
                'performance_summary': {
                    'avg_response_time': latest_performance.get('avg_response_time', 0),
                    'api_success_rate': latest_performance.get('api_success_rate', 0),
                    'error_rate': latest_performance.get('error_rate', 0)
                }
            }
            
            return {
                'success': True,
                'dashboard_data': dashboard_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard analytics: {str(e)}")
            raise ValueError(f"Dashboard analytics retrieval failed: {str(e)}")
    
    def schedule_report(self, schedule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule automatic report generation"""
        try:
            # Validate schedule configuration
            required_fields = ['report_type', 'schedule_frequency', 'recipients']
            for field in required_fields:
                if field not in schedule_config:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Generate schedule ID
            schedule_id = str(uuid.uuid4())
            
            # Create scheduled report
            scheduled_report = {
                'schedule_id': schedule_id,
                'report_type': schedule_config['report_type'],
                'schedule_frequency': schedule_config['schedule_frequency'],  # daily, weekly, monthly
                'recipients': schedule_config['recipients'],
                'format': schedule_config.get('format', ReportFormat.PDF.value),
                'created_at': datetime.utcnow().isoformat(),
                'created_by': schedule_config.get('user_id', 'system'),
                'next_run': self._calculate_next_run(schedule_config['schedule_frequency']),
                'status': 'active',
                'last_run': None,
                'run_count': 0
            }
            
            # Store scheduled report
            self.scheduled_reports[schedule_id] = scheduled_report
            
            return {
                'success': True,
                'schedule_id': schedule_id,
                'scheduled_report': scheduled_report
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling report: {str(e)}")
            raise ValueError(f"Report scheduling failed: {str(e)}")
    
    def _calculate_next_run(self, frequency: str) -> str:
        """Calculate next run time for scheduled report"""
        now = datetime.utcnow()
        
        if frequency == 'daily':
            next_run = now + timedelta(days=1)
        elif frequency == 'weekly':
            next_run = now + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)  # Default to daily
        
        return next_run.isoformat()
    
    def export_report(self, report_id: str, format: str = 'json') -> Dict[str, Any]:
        """Export report in specified format"""
        try:
            if report_id not in self.reports:
                return {
                    'success': False,
                    'error': 'Report not found'
                }
            
            report = self.reports[report_id]
            
            if format.lower() == 'json':
                return {
                    'success': True,
                    'format': 'json',
                    'data': report['data']
                }
            elif format.lower() == 'csv':
                # Simplified CSV export
                csv_data = self._convert_to_csv(report['data'])
                return {
                    'success': True,
                    'format': 'csv',
                    'data': csv_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Export format {format} not supported'
                }
            
        except Exception as e:
            self.logger.error(f"Error exporting report: {str(e)}")
            raise ValueError(f"Report export failed: {str(e)}")
    
    def _convert_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Convert report data to CSV format (simplified)"""
        # This is a simplified CSV conversion
        # In production, this would be more sophisticated
        csv_lines = []
        csv_lines.append("Report,Value")
        csv_lines.append(f"Title,{report_data.get('title', '')}")
        csv_lines.append(f"Period,{report_data.get('period', '')}")
        
        return "\n".join(csv_lines)

