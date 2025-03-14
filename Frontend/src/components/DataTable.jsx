import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import { useSearchParams } from "react-router-dom";

const DataTable = () => {
  const [data, setData] = useState([]);
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session_id");

  useEffect(() => {
    if (!sessionId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData((prevData) => [...prevData, ...newData]);
    };

    ws.onerror = (error) => console.error("WebSocket Error:", error);

    return () => ws.close();
  }, [sessionId]);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
        Real-Time Data Table
      </h2>
      <div className="overflow-hidden rounded-lg shadow-lg">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
              {/* <th className="p-3 text-left">Index</th> */}
              <th className="p-3 text-left">Flash Flood Confidence</th>
              <th className="p-3 text-left">Normal Flow Confidence</th>
              <th className="p-3 text-left">Not Flash Flood Confidence</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <AnimatePresence>
              {data.map((row, index) => (
                <motion.tr
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="hover:bg-gray-100 transition-all"
                >
                  <td className="p-3">{row[Object.keys(row)[0]]}</td>
                  <td className="p-3">{row[Object.keys(row)[1]]}</td>
                  <td className="p-3">{row[Object.keys(row)[2]]}</td>
                  <td className="p-3">{row[Object.keys(row)[3]]}</td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;
