import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from 'react-router-dom';
import Navbar from '../navbar/navbar';
import './DatasetDetails.css';
import { useNavigate } from 'react-router-dom';
;

function DatasetDetails() {
  const [dataset, setDataset] = useState(null);
  const [prompts, setPrompts] = useState([]);
  const [datasetRows, setDatasetRows] = useState([]);
  const [textValue, setTextValue] = useState("");
  const [error, setError] = useState("");
  const { id } = useParams();
  const navigate = useNavigate();
  

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8080/dataset/${id}/`);
        setDataset(response.data);
        setPrompts(response.data.prompts);
        setDatasetRows(response.data.dataset_rows);  // Update dataset rows
      } catch (error) {
        console.error("Error fetching dataset:", error);
      }
    };

    fetchData();
  }, [id]);

 

  const handleKeyPress = async (e) => {
    if (e.key === "Enter") {
      setError("");
      const trimmedPrompt = textValue.trim();

      if (!trimmedPrompt) {
        setError("Prompt cannot be empty.");
        return;
      }

      function getCookie(name) {
        const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
      }

      try {
        const csrfToken = getCookie('csrftoken');

        const response = await axios.post(`http://localhost:8080/dataset/${id}/`, {
          prompt: trimmedPrompt,
      }, {
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken,  // CSRF token from the cookie
          },
          withCredentials: true,  // Make sure cookies are sent with the request
      });

      const prompt_id = response.data['prompt_id'];
      const dataset_id = id;

        setTextValue("");

        navigate(`/result/dataset/${dataset_id}/prompt/${prompt_id}`);  


      } catch (error) {
        setError(error.response?.data?.error || "Failed to save prompt.");
      }
    }
  };

  // Function to handle click on a prompt and set its value in the input field
  const handlePromptClick = (promptText) => {
    setTextValue(promptText);
  };

  return (
    <div>
      <Navbar />
      {dataset ? (
        <>
          <div className='prompt_input'>
            <input
              type="text"
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type a prompt and press Enter to perform LLM Evaluation"
            />
            {error && <p style={{ color: "red" }}>{error}</p>}
          </div>

          <div className="prompts">
            {prompts.map((prompt, index) => (
              <div key={index} onClick={() => handlePromptClick(prompt.prompt_template)}>
                {prompt.prompt_template}
              </div>
            ))}
          </div>

          <div className="table">
            <table>
              <thead>
                <tr>
                  {datasetRows.length > 0 &&
                    Object.keys(datasetRows[0]).map((col, index) => (
                      <th key={index}>{col}</th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {datasetRows.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, idx) => (
                      <td key={idx}>{value}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <p>Loading dataset details...</p>
      )}
    </div>
  );
}

export default DatasetDetails;
