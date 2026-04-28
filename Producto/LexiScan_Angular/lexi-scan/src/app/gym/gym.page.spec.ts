import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { GymPage } from './gym.page';

describe('GymPage', () => {
  let component: GymPage;
  let fixture: ComponentFixture<GymPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GymPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(GymPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
