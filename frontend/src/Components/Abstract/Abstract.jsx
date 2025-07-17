import React, { useState } from 'react';
import './Abstract.css';

const Abstract = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    country: '',
    institution: '',
    field: '',
    year: '',
    title: '',
    abstract: '',
    keywords: '',
    pdf: null,
  });

  const [status, setStatus] = useState({ message: '', error: false, loading: false });

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ message: '', error: false, loading: true });

    try {
      const data = new FormData();
      for (const key in formData) {
        data.append(key, formData[key]);
      }

      const response = await fetch('http://localhost:5000/api/submit', {
        method: 'POST',
        body: data,
      });

      const result = await response.json();

      if (response.ok) {
        setStatus({ message: 'Abstract submitted successfully!', error: false, loading: false });
        setFormData({
          fullName: '',
          email: '',
          country: '',
          institution: '',
          field: '',
          year: '',
          title: '',
          abstract: '',
          keywords: '',
          pdf: null,
        });
      } else {
        setStatus({ message: result.message || 'Submission failed.', error: true, loading: false });
      }
    } catch (error) {
      setStatus({ message: 'An error occurred. Please try again.', error: true, loading: false });
    }
  };

  return (
    <div className="submit-container">
      <h2>Submit Your Abstract</h2>
      {status.message && (
        <div className={status.error ? 'error-message' : 'success-message'}>
          {status.message}
        </div>
      )}
      <form onSubmit={handleSubmit} className="submit-form" encType="multipart/form-data">
        <input type="text" name="fullName" placeholder="Full Name" value={formData.fullName} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
        <input type="text" name="country" placeholder="Country" value={formData.country} onChange={handleChange} />
        <input type="text" name="institution" placeholder="Institution" value={formData.institution} onChange={handleChange} />
        <select name="field" value={formData.field} onChange={handleChange} required>
          <option value="">Select Field</option>
          <option value="Public Health">Public Health</option>
          <option value="Agriculture">Agriculture</option>
          <option value="Mining Engineering">Mining Engineering</option>
          <option value="Technology / ICT">Technology / ICT</option>
          <option value="Artificial Intelligence">Artificial Intelligence</option>
        </select>
        <input type="number" name="year" placeholder="Year of Research" value={formData.year} onChange={handleChange} />
        <input type="text" name="title" placeholder="Abstract Title" value={formData.title} onChange={handleChange} required />
        <textarea name="abstract" placeholder="Abstract Body (or upload PDF)" value={formData.abstract} onChange={handleChange}></textarea>
        <input type="file" name="pdf" accept=".pdf" onChange={handleChange} />
        <input type="text" name="keywords" placeholder="Keywords (comma-separated)" value={formData.keywords} onChange={handleChange} />
        <button type="submit" disabled={status.loading}>
          {status.loading ? 'Submitting...' : 'Submit Abstract'}
        </button>
      </form>
    </div>
  );
};

export default Abstract;
