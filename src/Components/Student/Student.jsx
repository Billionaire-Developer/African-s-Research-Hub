// StudentDashboard.jsx
import React, { useEffect, useState } from 'react';
import './Student.css';

const Student = () => {
  const [activeTab, setActiveTab] = useState('submissions');
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    // Simulate API fetch
    setSubmissions([
      { id: 1, title: 'AI in Agriculture', status: 'Accepted', payment: 'Pending' },
      { id: 2, title: 'Climate Resilience', status: 'Under Review', payment: '-' },
      { id: 3, title: 'Public Health Access', status: 'Rejected', payment: '-' },
      { id: 4, title: 'Digital Finance Study', status: 'Published', payment: 'Paid' }
    ]);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'submissions':
        return (
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub) => (
                <tr key={sub.id}>
                  <td>{sub.title}</td>
                  <td>{sub.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        );

      case 'payment':
        return (
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Payment Status</th>
                <th>Invoice</th>
              </tr>
            </thead>
            <tbody>
              {submissions
                .filter((sub) => sub.status === 'Accepted' || sub.status === 'Published')
                .map((sub) => (
                  <tr key={sub.id}>
                    <td>{sub.title}</td>
                    <td>{sub.payment}</td>
                    <td>
                      {sub.payment === 'Pending' ? (
                        <button className="pay-btn">Pay Now</button>
                      ) : (
                        'Paid'
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        );

      case 'resubmission':
        return (
          <div>
            <h4>Resubmission Area</h4>
            {submissions.filter((sub) => sub.status === 'Rejected').length === 0 ? (
              <p>No rejected entries to resubmit.</p>
            ) : (
              submissions
                .filter((sub) => sub.status === 'Rejected')
                .map((sub) => (
                  <div key={sub.id} className="resubmit-box">
                    <p>{sub.title}</p>
                    <button className="resubmit-btn">Resubmit</button>
                  </div>
                ))
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dashboard-container">
      <h2>Student Dashboard</h2>
      <div className="tab-buttons">
        <button onClick={() => setActiveTab('submissions')} className={activeTab === 'submissions' ? 'active' : ''}>My Submissions</button>
        <button onClick={() => setActiveTab('payment')} className={activeTab === 'payment' ? 'active' : ''}>Payment Status</button>
        <button onClick={() => setActiveTab('resubmission')} className={activeTab === 'resubmission' ? 'active' : ''}>Resubmission Area</button>
      </div>
      <div className="tab-content">{renderTabContent()}</div>
    </div>
  );
};

export default Student;