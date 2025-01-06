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


  const calculateAverage = (key) => {
    const total = data.reduce((sum, item) => sum + parseFloat(item[key] || 0), 0);
    return total / data.length;
  };


  const avgGroqCorrectness = calculateAverage('groq_correctness');
  const avgGroqFaithfulness = calculateAverage('groq_faithfulness');
  const avgGeminiCorrectness = calculateAverage('gemini_correctness');
  const avgGeminiFaithfulness = calculateAverage('gemini_faithfulness');

  if (loading) 
    return (
      <>
      <Navbar />
      <div className="flex blue">Loading...</div>
      </>
      );

  if (error) 
    return (
      <>
      <Navbar />
      <div className="flex red">Error: {error}</div>);
      </>
    )

  return (
    <>
    <Navbar />
     <div className="table-section">
      <h2 className="heading">Results</h2>
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


    <div className="stats_heading"><h2>Average Stats</h2></div>
    <div className="average_stats">
    <table>
        <thead>
          <tr>
            <th></th>
            <th>Groq</th>
            <th>Gemini</th>
          </tr>
        </thead>
        <tbody>
            <tr>
              <td className="green">Correctness</td>
              <td>{avgGroqCorrectness}</td>
              <td>{avgGeminiCorrectness}</td>
            </tr>
        </tbody>

        <tbody>
            <tr>
              <td className="green">Faithfullness</td>
              <td>{avgGroqFaithfulness}</td>
              <td>{avgGeminiFaithfulness}</td>
            </tr>
        </tbody>
      </table>
    </div>
    </>
   
  );
};

export default resultPage;
