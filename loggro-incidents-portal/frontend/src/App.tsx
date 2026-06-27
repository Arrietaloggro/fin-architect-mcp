import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { IncidentForm } from './pages/IncidentForm';
import { Confirmation } from './pages/Confirmation';
import { Admin } from './pages/Admin';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route path="/" element={<IncidentForm />} />
          <Route path="/confirmation" element={<Confirmation />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
        <footer className="text-center py-6 text-xs text-gray-400 border-t border-gray-100 mt-8">
          Portal Interno de Incidencias — Loggro © {new Date().getFullYear()}
          <span className="mx-2">·</span>
          Solo para uso de equipos internos @loggro.com
        </footer>
      </div>
    </BrowserRouter>
  );
}
