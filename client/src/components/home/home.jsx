
import React, { useState } from "react";
import axios from "axios";
import Navbar from '../navbar/navbar'
import "./home.css"
import { useNavigate } from 'react-router-dom';


const home = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState("");
  const navigate = useNavigate();


  const handleFileChange = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.type === "text/csv") {
      setFile(uploadedFile);
      setError("");
    } else {
      setError("Please upload a valid CSV file.");
      setFile(null);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      setError("No file selected.");
      return;
    }
    setLoading(true);

    const formData = new FormData();
    formData.append("csv", file);

    try {
      
      const response = await axios.post("http://localhost:8080/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });


      let dataset_id = response.data.dataset.id
    
      navigate(`/dataset/${dataset_id}`);  

      setResponseMessage(response.data.message);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError("Error uploading file: " + err.message);
      setLoading(false);
    }
  };

  return (
    <>
    <Navbar/>
    <div className="upload">
      <h2>Upload CSV File</h2>
      <h4>CSV File must contain Input, Output and Meta columns</h4>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleFileUpload} disabled={!file || loading}>
        {loading ? "Uploading..." : "Upload and Send to Backend"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {responseMessage && <p>{responseMessage}</p>}
    </div>
    </>
    
  );
};

export default home;
