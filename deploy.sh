#!/bin/bash
source .env

export LIVEKIT_URL=$LIVEKIT_URL
export LIVEKIT_API_KEY=$LIVEKIT_API_KEY
export LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET

lk agent create
