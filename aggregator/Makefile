clear:
	@rm -f aggregator.zip
	@echo "Done!!"

clean: clear

zip:
	@zip aggregator.zip lambda_function.py config.yaml
	@echo "Done!!"

upload:
	@aws s3 cp aggregator.zip s3://nina-files/lambda/aggregator.zip
	@echo "Done!!"

update: zip upload
	@aws lambda update-function-code --function-name aggregator --s3-bucket nina-files --s3-key lambda/aggregator.zip
	@echo "Done!!"
