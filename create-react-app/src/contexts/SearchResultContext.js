// // SearchResultContext.js

// import React, { createContext, useContext, useState } from 'react';

// const SearchResultContext = createContext();

// export const SearchResultProvider = ({ children }) => {
//   const [searchResults, setSearchResults] = useState([]);

//   const setResults = (results) => {
//     setSearchResults(results);
//   };

//   return (
//     <SearchResultContext.Provider value={{ searchResults, setResults }}>
//       {children}
//     </SearchResultContext.Provider>
//   );
// };

// export const useSearchResult = () => {
//   return useContext(SearchResultContext);
// };

// SearchResultContext.js
import { createContext, useContext, useState } from 'react';

const SearchResultContext = createContext();

export const useSearchResult = () => useContext(SearchResultContext);

export const SearchResultProvider = ({ children }) => {
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const setResults = (results) => {
    setSearchResults(results);
    setIsLoading(false);
  };

  const setLoading = (loading) => {
    setIsLoading(loading);
  };

  return (
    <SearchResultContext.Provider value={{ searchResults, setResults, isLoading, setLoading }}>
      {children}
    </SearchResultContext.Provider>
  );
};
