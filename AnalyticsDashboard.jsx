import React from 'react';

export function AnalyticsDashboard() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Analytics Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-2">Total Tax Paid</h3>
          <p className="text-3xl font-bold text-blue-600">€12,450</p>
          <p className="text-sm text-gray-600">This year</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-2">Potential Savings</h3>
          <p className="text-3xl font-bold text-green-600">€2,340</p>
          <p className="text-sm text-gray-600">Identified opportunities</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-2">Effective Tax Rate</h3>
          <p className="text-3xl font-bold text-purple-600">18.5%</p>
          <p className="text-sm text-gray-600">Average rate</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Monthly Tax Breakdown</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <p className="text-gray-500">Chart placeholder</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Deduction Categories</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>Business Expenses</span>
              <span className="font-medium">€3,200</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Professional Development</span>
              <span className="font-medium">€1,800</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Home Office</span>
              <span className="font-medium">€1,200</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

