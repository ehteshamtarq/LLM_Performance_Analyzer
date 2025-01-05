import React, { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import axios from "axios";
import Navbar from '../navbar/navbar';
import './resultPage.css'



const resultPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { dataset_id, prompt_id } = useParams();

  useEffect(() => {

    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8080/result/${dataset_id}/${prompt_id}`); // Replace with your API endpoint
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); 

  if (loading) 
    return (
      <>
      <Navbar />
      <div className="flex">Loading...</div>
      </>
      );

  if (error) 
    return (
      <>
      <Navbar />
      <div className="flex">Error: {error}</div>);
      </>
    )

  return (
    <>
    <Navbar />
     <div className="table-section">
      <h2 className="heading">Responses Data</h2>
      <table style={{ width: "100%" }}>
        <thead>
          <tr>
            <th>Prompt</th>
            <th>Expected Answer</th>
            <th>Groq Response</th>
            <th>Gemini Response</th>
            <th>Groq Correctness</th>
            <th>Groq Faithfulness</th>
            <th>Gemini Correctness</th>
            <th>Gemini Faithfulness</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} >
              <td>{item.prompt}</td>
              <td>{item.expected_answer}</td>
              <td>{item.groq_response}</td>
              <td>{item.gemini_response}</td>
              <td>{item.groq_correctness}</td>
              <td>{item.groq_faithfulness}</td>
              <td>{item.gemini_correctness}</td>
              <td>{item.gemini_faithfulness}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </>
   
  );
};

export default resultPage;
