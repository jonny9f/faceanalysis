// File: src/App.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '@fontsource/inter';
import { CssVarsProvider, useColorScheme } from '@mui/joy/styles';
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import FormControl from '@mui/joy/FormControl';
import FormLabel from '@mui/joy/FormLabel';
import Input from '@mui/joy/Input';
import Button from '@mui/joy/Button';
import Link from '@mui/joy/Link';
import Grid from '@mui/joy/Grid';



function ModeToggle() {
  const { mode, setMode } = useColorScheme();
  const [mounted, setMounted] = React.useState(false);

  // necessary for server-side rendering
  // because mode is undefined on the server
  React.useEffect(() => {
    setMounted(true);
  }, []);
  if (!mounted) {
    return null;
  }

  return (
    <Button
      variant="outlined"
      onClick={() => {
        setMode(mode === 'light' ? 'dark' : 'light');
      }}
    >
      {mode === 'light' ? 'Turn dark' : 'Turn light'}
    </Button>
  );
}


function EmotionDisplay() {
  const [response, setResponse] = useState('');
  const videoRef = useRef(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      captureImageFromVideo();
    }, 200); // Adjust the interval as needed

    return () => clearInterval(interval);
  }, []);

  const captureImageFromVideo = () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d').drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    // Convert the canvas to a Blob directly
    canvas.toBlob(sendImageToServer, 'image/jpeg');
  };

  const sendImageToServer = (blob) => {
    const reader = new FileReader();
    try {
      reader.readAsDataURL(blob);
      reader.onloadend = () => {
        axios.post('/analyze', { image: reader.result })
          .then(response => {
            setResponse(JSON.stringify(response.data, null, 2));
          })
          .catch(console.error);
      };
    }
    catch {

    }
  };

  return (
    <div>
      <div style={{ maxWidth: '100%' }}>
        <video ref={videoRef} autoPlay muted style={{ maxWidth: '100%', height: 'auto' }}></video>
      </div>
      <div>
        <strong>Analysis Results:</strong>
        {response}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <CssVarsProvider defaultMode="dark">
      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        <Grid xs={2} >
 

        </Grid>
        <Grid xs={2}>
          <Sheet
            sx={{
              width: 650,
              mx: 'auto', // margin left & right
              my: 4, // margin top & bottom
              py: 3, // padding top & bottom
              px: 2, // padding left & right
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              borderRadius: 'sm',
              boxShadow: 'md',
            }}
          >
            <div>
              {/* <Typography level="h4" component="h1">
                Emotions
              </Typography> */}
            </div>
            <EmotionDisplay />

          </Sheet>

        </Grid>
      </Grid>
    </CssVarsProvider>
  )
}

