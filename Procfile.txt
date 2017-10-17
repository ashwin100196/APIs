web: python test_updated.py ${PORT}
port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)