# CCD Image Processing Application

A Python-based application for processing astronomical CCD images, built with Astropy and ccdproc.

## Overview

This project implements core astronomical image processing workflows based on the [Astropy CCD reduction guide](https://www.astropy.org/ccd-reduction-and-photometry-guide/). While following established reduction techniques, I'm developing my own interface and workflow to better understand the complete image processing pipeline from raw data to final results.

## Features

- **Image Management**: Load and organize lights, darks, bias, and flat frames
- **Master Frame Creation**: Generate master calibration frames (bias, dark, flat)
- **Image Calibration**: Apply calibration to light frames
- **Interactive Interface**: User-friendly GUI for processing workflow
- **Real-time Feedback**: Command log with operation history
