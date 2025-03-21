import React, { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import StreamingContentGenerator from '../components/StreamingContentGenerator';

export default function StreamingContentPage() {
  return (
    <Layout>
      <Head>
        <title>Streaming Content Generator | EduAI</title>
        <meta name="description" content="Generate educational content in real-time with AI" />
      </Head>
      
      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4" style={{ color: '#5e35b1' }}>Real-time Content Generator</h1>
            <p className="text-gray-600">
              Watch as AI generates educational content for you in real-time, powered by NVIDIA's Nemotron model.
            </p>
          </div>
          
          <StreamingContentGenerator />
        </div>
      </div>
    </Layout>
  );
}
