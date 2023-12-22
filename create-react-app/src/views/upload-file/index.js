import React, { useState } from "react";
import Modal from 'react-modal';
import LinearProgress from '@mui/material/LinearProgress';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import axios from "axios";
import MainCard from 'ui-component/cards/MainCard';
import { Typography } from '@mui/material';
import { useSearchResult } from '../../contexts/SearchResultContext';
// import { useEffect } from "react";


const App = () => {
  const [selectedFiles, setSelectedFiles] = useState([]); // Array to store selected files
  const [showMessage, setShowMessage] = useState("Indexing..")
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  // const { searchResults } = useSearchResult();
  const { searchResults, isLoading } = useSearchResult(); // useContext used here

  const onFileChange = (event) => {
    const files = Array.from(event.target.files);

    // Update the state to append newly selected files
    setSelectedFiles((prevSelectedFiles) => [...prevSelectedFiles, ...files]);
  };

  const onFileRemove = (index) => {
    // Update the state to remove the file at the specified index
    setSelectedFiles((prevSelectedFiles) => {
      const updatedFiles = [...prevSelectedFiles];
      updatedFiles.splice(index, 1);
      return updatedFiles;
    });
  };


  const onFileUpload = async () => {
    setIsUploading(true);

    try {
      // Create an array of formData for each selected file
      const formDataArray = selectedFiles.map((file) => {
        const formData = new FormData();
        formData.append("myFile", file, file.name);
        return formData;
      });

      // Perform multiple file uploads using Promise.all
      const responses = await Promise.all(
        formDataArray.map((formData) =>
          axios.post("http://127.0.0.1:8000/api/uploadfile", formData)
        )
      );

      // Handle responses as needed
      console.log(responses[0].data.message);
      
      // Show "Indexing successfully done" for 1 second
      setShowMessage("Indexing successfully done");
      setTimeout(() => {
        setIsUploading(false);
        setIsModalOpen(false);
      }, 1000);
      // setIsModalOpen(false);
    } catch (error) {
      console.error('Error uploading files:', error);
    }
    // finally {
    //   setIsUploading(false);
    // }
  };

  console.log(searchResults);

  const fileData = () => {
    if (selectedFiles.length > 0) {
      return (
        <div>
          <h2>File Details:</h2>
          {selectedFiles.map((file, index) => (
            <div key={index}>
              <p>File Name: {file.name}</p>
              <p>File Type: {file.type}</p>
              <p>Last Modified: {file.lastModifiedDate.toDateString()}</p>
              <button onClick={() => onFileRemove(index)}>Remove</button>
            </div>
          ))}
        </div>
      );
    } else {
      return (
        <div>
          <br />
          <h4>Choose before Pressing the Upload button</h4>
        </div>
      );
    }
  };

  return (
    <>
      <Modal
        isOpen={isModalOpen}
        onRequestClose={() => setIsModalOpen(false)}
        shouldCloseOnOverlayClick={false}
        style={{
          overlay: {
            backgroundColor: 'rgba(0, 0, 0, 0.65)',
            zIndex: 1400,
          },
          content: {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '400px',
            padding: '20px',
            borderRadius: '8px',
            backgroundColor: '#fff',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
            zIndex: 100,
          },
        }}
        ariaHideApp={false}
      >
        <div>
          <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>Upload files</h1>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <input
              type="file"
              multiple
              onChange={onFileChange}
              style={{
                width: 'calc(100% - 10px)',
                marginRight: '10px',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ccc',
              }}
            />
            
            <button
              style={{
                padding: '10px 20px',
                margin: '10px',
                backgroundColor: '#4caf50',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
              onClick={onFileUpload}
            >
              Upload!
            </button>
          </div>
        
          {isUploading && (
          <Box sx={{ width: '100%', marginTop: '10px' }}>
              
              <LinearProgress />
              <h3 style={{
                  textAlign: "center",
              }}>{showMessage}</h3>
          </Box>
        )}
        {!isUploading && isModalOpen && showMessage !== "Indexing.." && (
          <div style={{ textAlign: 'center', marginTop: '10px' }}>
            <h3>{showMessage}</h3>
          </div>
        )}

          {!isUploading && isModalOpen && fileData()}


        </div>
      </Modal>

      {/* {searchResults.map((result, index) => (
        <MainCard key={index} title={result.title} sx={{ mb: 2 }}>
          <Typography variant="body2">{result.text_chunk}</Typography>
        </MainCard>
      ))} */}
      {/* Loader */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <CircularProgress />
        </Box>
      )}

      {/* Search results */}
      {!isLoading && searchResults.map((result, index) => (
        <MainCard key={index} title={result.title} sx={{ mb: 2 }}>
          <Typography variant="body2">{result.text_chunk}</Typography>
        </MainCard>
      ))}
    </>          
  );
}

export default App;
