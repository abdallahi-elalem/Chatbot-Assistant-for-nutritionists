import { Container, Row } from 'react-bootstrap';
import { Feature, HeroSlider, Nav, Ubot } from '../components';
 

export default function Home() {
	return (
		<>
			<Nav />
			<HeroSlider />
			<Container>
				<Row>
					<Feature
						imageNo={0}
						color='#2196F3'
						bgColor={'#E3F2FD'}
						title={'RENDEZ VOUS'}
					/>
					<Feature
						imageNo={1}
						color='#673AB7'
						bgColor={'#EDE7F6'}
						title={'BIOCAPTEUR'}
					/>
					<Feature
						imageNo={2}
						color='#fdcd77'
						bgColor={'#f4deb7c2'}
						title={'SOINS À DOMICILE'}
					/>
					<Feature
						imageNo={3}
						color='#D72E9D'
						bgColor={'#dc94c354'}
						title={'TÉLÉCONSULTATION'}
					/>
				</Row>
			</Container>
			<Ubot />
		</>
	);
}
