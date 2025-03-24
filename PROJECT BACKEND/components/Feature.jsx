import styled from 'styled-components';
import rendezVousImage from '../assets/images/image1.jpg';
import biocapteurImage from '../assets/images/image7.jpg';
import soinsADomicileImage from '../assets/images/image5.jpg';
import teleconsultationImage from '../assets/images/image4.jpg';
import Image from 'next/image';

const images = [rendezVousImage, biocapteurImage, soinsADomicileImage, teleconsultationImage];

const Feature = ({ title, imageNo, color, bgColor }) => {
	const imageSrc = images[imageNo];

	return (
		<div style={{marginBottom:"120px"}}className='col-12 col-lg-3 col-md-6'>
			<CardWrapper>
				<div className='d-flex align-items-center'>
					<Box style={{ backgroundColor: `${bgColor}` }}>
						<Image src={imageSrc}   style={{ width: '10px', height: '50px' }} />
					</Box>
 				</div>
			</CardWrapper>
		</div>
	);
};

export default Feature;

const CardWrapper = styled.div`
	padding: 20px;
	border-radius: 8px;
	margin-top: 1.5rem !important;
	background-color: #fff;
	border: 1px solid #e3f2fd;
	transition: box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms;
	h5 {
		margin: 10px;
		font-size: 14px;
		color: rgb(33, 33, 33);
		font-weight: 500;
		line-height: 18px;
	}
	img {
		width: 0px;
		height: 0px;
	}
	&:hover {
		box-shadow: rgb(32 40 45 / 8%) 0px 2px 14px 0px;
	}
`;
const Box = styled.div`
	min-width: 150px;
	min-height: 12px;
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
`;
