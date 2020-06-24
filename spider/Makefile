clear:
	@rm -f spider.zip
	@echo "Done!!"

clean: clear

zip:
	@zip spider.zip lambda_function.py config.yaml
	@echo "Done!!"

upload:
	@aws s3 cp spider.zip s3://nina-files/lambda/spider.zip
	@echo "Done!!"

update: zip upload
	@aws lambda update-function-code --function-name spider --s3-bucket nina-files --s3-key lambda/spider.zip
	@echo "Done!!"
