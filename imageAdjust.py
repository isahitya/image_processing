import sys
import scipy
import numpy
from scipy import misc
import math

color_palette=[(0,0,0),(255,255,255),(200,0,0),(0,200,0),(0,0,200),(100,100,0),(0,100,100),(100,0,100)]

def truncate(color):
	if color<0: return 0
	if color>255: return 255
	return color

def find_nearest_color(givenColor):
	r,g,b=givenColor
	out=color_palette[0]
	dist=lambda c1,c2:((c1[0]-c2[0])*(c1[0]-c2[0]))+((c1[1]-c2[1])*(c1[1]-c2[1]))+((c1[2]-c2[2])*(c1[2]-c2[2]))
	minDist=dist(givenColor,color_palette[0])
	for color in color_palette[1:]:
		if dist(givenColor,color)<minDist:
			minDist=dist(givenColor,color)
			out=color
	print(out)
	return out

def quantize(image):
	h,w,b=image.shape
	newImage=numpy.zeros(image.shape)
	minDistAt=0
	for x in range(0,w):
		for y in range(0,h):
			newImage[y][x]=find_nearest_color(image[y][x])
	return newImage

def brighten(image,brightness):
	if brightness>255:brightness=255
	if birghtness<0:brightness=0
	brightness=brightness*255/100
	newImage=numpy.zeros(image.shape)
	for x in range(0,image.shape[1]):
		for y in range(0,image.shape[0]):
			newImage[y][x][0]=truncate(image[y][x][0]+brightness)
			newImage[y][x][1]=truncate(image[y][x][1]+brightness)
			newImage[y][x][2]=truncate(image[y][x][2]+brightness)
	return newImage

def contrast(image,contrast):
	if contrast>100:contrast=100
	if contrast<0:contrast=0
	contrast=contrast*255/100
	newImage=numpy.zeros(image.shape)
	factor=((259*(contrast+255))/(255*(259-contrast)))
	for x in range(0,image.shape[1]):
		for y in range(0,image.shape[0]):
			newImage[y][x][0]=truncate(factor*(image[y][x][0]-128)+128)
			newImage[y][x][1]=truncate(factor*(image[y][x][1]-128)+128)
			newImage[y][x][2]=truncate(factor*(image[y][x][2]-128)+128)
	return newImage


def convolute(image,boxW,boxH):
	h,w,b=image.shape
	newImage=numpy.zeros((h,w,b))
	for x in range(0,newImage.shape[1]):
		for y in range(0,newImage.shape[0]):
			blurredPixel=[0,0,0]
			xlb=max(0,x-int(boxW/2))
			xub=min(image.shape[1]-1,x+int(boxW/2)+1)
			ylb=max(0,y-int(boxH/2))
			yub=min(image.shape[0]-1,y+int(boxH/2)+1)
			for i in range(xlb,xub):
				for j in range(ylb,yub):
					blurredPixel+=image[j][i]/((xub-xlb)*(yub-ylb))
			newImage[y][x]=blurredPixel
	return newImage

#def getBlurredPixel(image,x,y,kernelW,kernelH):
#	mean=[0,0,0]
#	for i in range(x-int(boxW/2),x+int(boxW/2+1)):
#		for j in range(y-int(boxH/2),y+int(boxH/2)+1):
#			if j<0:
#				j=0
#			elif j>=image.shape[0]:
#				j=image.shape[0]-1
#			if i<0:
#				i=0
#			elif i>=image.shape[1]:
#				i=image.shape[1]-1
			
#			mean+=(image[j][i])/(boxW*boxH)
#	return mean

gaussKernel=[
1/16,1/8,1/16,
1/8,1/4,1/8,
1/16,1/8,1/16
]

def gaussBlur(image):
	newImage=numpy.zeros(image.shape)
	for x in range(0,newImage.shape[1]):
		for y in range(0,newImage.shape[0]):
			blurredPixel=[0,0,0]
			k=0
			for i in range(x-1,x+1+1):
				for j in range(y-1,y+1+1):
					if i<0:i=0
					elif i>=image.shape[1]:i=image.shape[1]-1
					if j<0:j=0
					elif j>=image.shape[0]:j=image.shape[0]-1
					blurredPixel+=image[j][i]*gaussKernel[k]
					k+=1
			newImage[y][x]=blurredPixel
	return newImage
		

def boxBlur(image):
	newImage=numpy.zeros(image.shape)
	for x in range(0,newImage.shape[1]):
		for y in range(0,newImage.shape[0]):
			blurredPixel=[0,0,0]
			for i in range(x-1,x+1+1):
				for j in range(y-1,y+1+1):
					if i<0:i=0
					elif i>=image.shape[1]:i=image.shape[1]-1
					if j<0:j=0
					elif j>=image.shape[0]:j=image.shape[0]-1
					blurredPixel+=image[j][i]/9
			newImage[y][x]=blurredPixel
	return newImage
		

def sharpen(image,amount):
	newImage=image.copy()
	blurredImage=boxBlur(newImage,2)
	fine=numpy.zeros(image.shape)
	for x in range(0,fine.shape[1]):
		for y in range(0,fine.shape[0]):
			fine[y][x]=image[y][x]-blurredImage[y][x]
	for x in range(0,newImage.shape[1]):
		for y in range(0,newImage.shape[0]):
			newImage[y][x][0]=truncate(image[y][x][0]+fine[y][x][0]*amount)
			newImage[y][x][1]=truncate(image[y][x][1]+fine[y][x][1]*amount)
			newImage[y][x][2]=truncate(image[y][x][2]+fine[y][x][2]*amount)
	return newImage


def changeOpacity(image,alpha):
        newImage=numpy.zeros((image.shape))#(image.shape[0],image.shape[1],4)
        for x in range(0,image.shape[1]):
                for y in range(0,image.shape[0]):
                        newImage[y][x]=image[y][x]
                        newImage[y][x][3]=alpha
        return newImage

def rotate(image,angle,cw=False):#The code for rotation till 180 degree worked as expected but for further rotation some unexpected changes are made,The image is conceptually flipped(by taking Y=-Y and X=-X) and the angle used is (angle-180)	

	if cw==True:angle=360-angle
	h,w,b=image.shape
	H,W=h,w
	angleGreaterThan180=False
	if angle>180:
		angleGreaterThan180=True
		angle-=180
	theta=angle
	if(angle>90):
		H=w
		W=h
		theta=angle-90
	nw=abs(int((W*math.cos(theta*math.pi/180))+(H*math.sin(theta*math.pi/180))))
	nh=abs(int((W*math.sin(theta*math.pi/180))+(H*math.cos(theta*math.pi/180))))
	
#	newImage=numpy.zeros((nh,nw,4))# This line is to use trasparent pixel insted of black to fill stray locations in new image
	newImage=numpy.zeros((nh,nw,3))
	midx=int(image.shape[1]/2)# These 4 lines are to rotate about the center
	midy=int(image.shape[0]/2)#               
	newMidx=int(newImage.shape[1]/2)#
	newMidy=int(newImage.shape[0]/2)#
#	midx=0                    #These 4 lines are to rotate about a particular point
#	midy=int(image.shape[0]-60)#
#	newMidx=0#
#	newMidy=int(newImage.shape[0]-60)#
	for x in range(0,newImage.shape[1]):
		for y in range(0,newImage.shape[0]):
			uX=x-newMidx
			uY=y-newMidy
			X=int((uX*math.cos(angle*math.pi/180))-(uY*math.sin(angle*math.pi/180)))
			Y=int((uX*math.sin(angle*math.pi/180))+(uY*math.cos(angle*math.pi/180)))
			X=X+midx
			Y=Y+midy		
			if X>=0 and Y>=0 and X<image.shape[1] and Y<image.shape[0]:
				if(angleGreaterThan180):newImage[y][x]=image[-Y][-X]
				else:newImage[y][x]=image[Y][X]
	return newImage
		
def blendPixel(B,A,mode):
	if mode=='normal':return B
	elif mode=='alpha':
		arr=numpy.empty((4),dtype=numpy.uint8)
		p,q=A[3]/255,(B[3]/255)*(1-(A[3]/255))
		
		arr[0]=min((int(A[0])*p)+int(B[0]*q),255)
		arr[1]=min((int(A[1])*p)+int(B[1]*q),255)
		arr[2]=min((int(A[2])*p)+int(B[2]*q),255)
		arr[3]=255
		return arr
	elif mode=='add':
		arr=numpy.empty((4))
		arr[0]=min(255,int(A[0])+int(B[0]))
		arr[1]=min(255,int(A[1])+int(B[1]))
		arr[2]=min(255,int(A[2])+int(B[2]))
		arr[3]=A[3]
		return arr


def blend(imageA,imageB,x,y,mode='normal'):
	newImage=numpy.zeros(imageA.shape)
	for i in range(0,newImage.shape[1]):
		for j in range(0,newImage.shape[0]):
			pixel=imageA[j][i]
			if i>=x and abs(i-x)<imageB.shape[1] and i<imageA.shape[1]:
				if j>=y and abs(j-y)<imageB.shape[0] and j<imageA.shape[0]:
					pixel=blendPixel(imageA[j][i],imageB[j-y][i-x],mode)
			newImage[j][i]=pixel
	return newImage


def main():
	if len(sys.argv)==1:
		print("Bhai file ka naam to de")
		sys.exit(0)
	image=misc.imread(sys.argv[1],mode='RGB')
#	image=misc.imread(sys.argv[1],mode='RGBA')
	name,extension=sys.argv[1].split('.')
#	imageB=changeOpacity(misc.imread(sys.argv[2],mode='RGBA'),150)
#	misc.imsave("blend"+name,blend(image,imageB,int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]),'png')
	if len(sys.argv)==4 and sys.argv[3]=='cw':
		misc.imsave("rotated"+name,rotate(image,int(sys.argv[2]),True),'png')
	else: misc.imsave("rotated"+name,rotate(image,int(sys.argv[2])),'png')

if __name__=='__main__':
	main()
