import React, { useState, useEffect } from 'react';
import { BarChart3, Download, RefreshCw, CheckCircle, XCircle, Clock, TrendingUp, Eye, Filter, Search } from 'lucide-react';

const EvaluationDashboard = () => {
  const [testResults, setTestResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedTest, setSelectedTest] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    passed: 0,
    failed: 0,
    accuracy: 0,
    avgConfidence: 0
  });

  useEffect(() => {
    fetchTestResults();
  }, []);

  const fetchTestResults = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/evaluation/results');
      const data = await response.json();
      setTestResults(data.results || []);
      setStats(data.stats || {
        total: 0,
        passed: 0,
        failed: 0,
        accuracy: 0
      });
    } catch (error) {
      console.error('Error fetching test results:', error);
      // Mock data for demo
      const mockResults = [
        {
          id: 1,
          input: "I spoke with customer Amit Verma today. His phone number is nine nine eight eight seven seven six six five five. He stays at 45 Park Street, Salt Lake, Kolkata. We discussed the demo and next steps.",
          expected: {
            customer: {
              full_name: "Amit Verma",
              phone: "9988776655",
              address: "45 Park Street",
              city: "Kolkata",
              locality: "Salt Lake"
            },
            interaction: {
              summary: "Discussed demo and next steps",
              created_at: "2026-01-18T11:30:00Z"
            }
          },
          actual: {
            customer: {
              full_name: "Amit Verma",
              phone: "9988776655",
              address: "45 Park Street",
              city: "Kolkata",
              locality: "Salt Lake"
            },
            interaction: {
              summary: "Discussed demo and next steps",
              created_at: "2026-01-18T11:30:00Z"
            }
          },
          passed: true,
          confidence: 0.95,
          timestamp: "2026-01-20T10:30:00Z"
        },
        {
          id: 2,
          input: "Customer Sarah Johnson called from 9876543210. She lives at 123 Main Road, Bandra, Mumbai. We talked about pricing options.",
          expected: {
            customer: {
              full_name: "Sarah Johnson",
              phone: "9876543210",
              address: "123 Main Road",
              city: "Mumbai",
              locality: "Bandra"
            },
            interaction: {
              summary: "Talked about pricing options",
              created_at: "2026-01-20T11:00:00Z"
            }
          },
          actual: {
            customer: {
              full_name: "Sarah Johnson",
              phone: "9876543210",
              address: "123 Main Road",
              city: "Mumbai",
              locality: "Bandra"
            },
            interaction: {
              summary: "Discussed pricing options",
              created_at: "2026-01-20T11:00:00Z"
            }
          },
          passed: true,
          confidence: 0.88,
          timestamp: "2026-01-20T11:05:00Z"
        }
      ];
      setTestResults(mockResults);
      setStats({
        total: mockResults.length,
        passed: mockResults.filter(r => r.passed).length,
        failed: mockResults.filter(r => !r.passed).length,
        accuracy: (mockResults.filter(r => r.passed).length / mockResults.length * 100).toFixed(1),
        avgConfidence: (mockResults.reduce((sum, r) => sum + r.confidence, 0) / mockResults.length * 100).toFixed(1)
      });
    } finally {
      setIsLoading(false);
    }
  };

  const runTests = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/evaluation/run', {
        method: 'POST'
      });
      await fetchTestResults();
    } catch (error) {
      console.error('Error running tests:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadResults = () => {
    const csvContent = [
      ['Test ID', 'Input', 'Expected Output', 'Actual Output', 'Passed', 'Confidence', 'Timestamp'],
      ...filteredResults.map(test => [
        test.id,
        `"${test.input}"`,
        JSON.stringify(test.expected),
        JSON.stringify(test.actual),
        test.passed ? 'PASS' : 'FAIL',
        test.confidence,
        test.timestamp
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation-results-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const filteredResults = testResults.filter(test => {
    const matchesSearch = (test.input && test.input.toLowerCase().includes(searchTerm.toLowerCase())) ||
                          (test.id && `#${test.id}`.includes(searchTerm));
    const matchesFilter = filterStatus === 'all' || 
                          (filterStatus === 'passed' && test.passed) ||
                          (filterStatus === 'failed' && !test.passed);
    return matchesSearch && matchesFilter;
  });

  const viewTestDetails = (test) => {
    setSelectedTest(test);
    setShowDetails(true);
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-lg">Loading evaluation results...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 space-y-4 md:space-y-0">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-800">Evaluation Dashboard</h2>
          </div>
          <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-3">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search tests..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Tests</option>
                <option value="passed">Passed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            <button
              onClick={runTests}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Run Tests</span>
            </button>
            <button
              onClick={downloadResults}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download CSV</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Tests</p>
                <p className="text-2xl font-bold text-blue-800">{stats.total}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium">Passed</p>
                <p className="text-2xl font-bold text-green-800">{stats.passed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-600 font-medium">Failed</p>
                <p className="text-2xl font-bold text-red-800">{stats.failed}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">Accuracy</p>
                <p className="text-2xl font-bold text-purple-800">{stats.accuracy}%</p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600 font-medium">Avg Confidence</p>
                <p className="text-2xl font-bold text-orange-800">{stats.avgConfidence}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Test Results</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Input</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredResults.map((test) => (
                <tr key={test.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{test.id}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="max-w-xs truncate" title={test.input || 'No input'}>
                      {test.input || 'No input'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {test.passed ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        PASS
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <XCircle className="w-3 h-3 mr-1" />
                        FAIL
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.confidence ? (test.confidence * 100).toFixed(1) + '%' : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.timestamp ? new Date(test.timestamp).toLocaleString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => viewTestDetails(test)}
                      className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showDetails && selectedTest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold">Test Details - #{selectedTest.id}</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Input Text</h4>
                <p className="text-gray-600 bg-gray-50 p-3 rounded">{selectedTest.input || 'No input available'}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Expected Output</h4>
                  <pre className="text-sm text-gray-600 bg-green-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedTest.expected, null, 2)}
                  </pre>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Actual Output</h4>
                  <pre className="text-sm text-gray-600 bg-blue-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedTest.actual, null, 2)}
                  </pre>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  selectedTest.passed 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {selectedTest.passed ? (
                    <><CheckCircle className="w-4 h-4 mr-1" /> PASS</>
                  ) : (
                    <><XCircle className="w-4 h-4 mr-1" /> FAIL</>
                  )}
                </span>
                <span className="text-sm text-gray-600">
                  Confidence: {selectedTest.confidence ? (selectedTest.confidence * 100).toFixed(1) + '%' : 'N/A'}
                </span>
                <span className="text-sm text-gray-600">
                  {selectedTest.timestamp ? new Date(selectedTest.timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvaluationDashboard;
