import React from 'react';

export function ComplianceCenter() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Compliance Center</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Tax Deadlines</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded">
              <div>
                <p className="font-medium">Income Tax Return</p>
                <p className="text-sm text-gray-600">Malta 2024</p>
              </div>
              <span className="text-yellow-600 font-medium">Due: Jun 30</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded">
              <div>
                <p className="font-medium">VAT Return Q1</p>
                <p className="text-sm text-gray-600">Malta 2024</p>
              </div>
              <span className="text-green-600 font-medium">Completed</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Compliance Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>Tax Registration</span>
              <span className="text-green-600">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span>VAT Registration</span>
              <span className="text-green-600">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Social Security</span>
              <span className="text-green-600">✓ Up to date</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

